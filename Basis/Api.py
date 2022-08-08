#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from gevent import pywsgi
from Checker import formatCheck
from Basis.Logger import logging
from Basis.Manager import Manager
from flask import Flask, Response, request
from Basis.Exception import managerException
from Basis.Constant import ApiPort, ApiPath, ApiToken, Version

webApi = Flask(__name__)  # init flask server


def formatProxy(raw: str or dict) -> dict:
    from Filter import Filter
    from ProxyDecoder import decode
    if type(raw) == str:
        raw = decode(raw)
        if raw is None:
            raise RuntimeError('decode error')
    try:
        return {
            'type': raw['type'],
            'name': raw['info']['remark'] if 'remark' in raw['info'] else '',
            'info': Filter(raw['type'], raw['info'])
        }
    except:
        raise RuntimeError('filter error')


def jsonResponse(data: dict) -> Response:  # return json mime
    return Response(json.dumps(data), mimetype = 'application/json')


def genError(message: str) -> Response:
    return jsonResponse({
        'success': False,
        'message': message,
    })


def tokenCheck() -> bool:
    if ApiToken == '': return True  # without token check
    if request.method == 'GET':
        return request.args.get('token') == ApiToken
    elif request.method == 'POST':
        return request.json.get('token') == ApiToken
    else:
        return False  # polyfill


@webApi.route(os.path.join(ApiPath, 'task'), methods = ['GET'])
def getTaskList() -> Response:
    if not tokenCheck():  # token check
        return genError('Invalid token')
    taskList = Manager.listUnion()
    logging.debug('API get task list -> %s' % taskList)
    return jsonResponse({
        'success': True,
        'task': taskList,
    })


@webApi.route(os.path.join(ApiPath, 'task'), methods = ['POST'])
def createTask() -> Response:
    if not tokenCheck():  # token check
        return genError('Invalid token')

    try:
        # TODO: format check and proxy list
        checkList = formatCheck(request.json.get('check'))
    except:
        return genError('Some error in check options')
    proxyList = []
    for proxy in request.json.get('proxy'):
        try:
            proxyList.append(formatProxy(proxy))
        except Exception as exp:
            return genError('Proxy error in %s -> %s' % (proxy, exp))

    logging.debug('API create task -> check = %s | proxy = %s' % (checkList, proxyList))
    tasks = []
    for proxy in proxyList:
        tasks.append({
            **proxy,
            'check': checkList  # load check items
        })
    checkId = Manager.addUnion(tasks)  # add into manager -> get id
    logging.debug('API return task id -> %s' % checkId)
    return jsonResponse({
        'success': True,
        'id': checkId,
        'check': checkList,
        'proxy': proxyList,
    })


@webApi.route(os.path.join(ApiPath, 'task/<taskId>'), methods = ['GET'])
def getTaskInfo(taskId: str) -> Response:
    if not tokenCheck():  # token check
        return genError('Invalid token')
    logging.debug('API get task -> %s' % taskId)
    if not Manager.isUnion(taskId):
        return genError('Task not found')
    return jsonResponse({
        'success': True,
        **Manager.getUnion(taskId)
    })


@webApi.route(os.path.join(ApiPath, 'task/<taskId>'), methods = ['DELETE'])
def deleteTask(taskId: str) -> Response:
    if not tokenCheck():  # token check
        return genError('Invalid token')
    logging.debug('API get task -> %s' % taskId)
    if not Manager.isUnion(taskId):
        return genError('Task not found')
    try:
        Manager.delUnion(taskId)
        return jsonResponse({
            'success': True
        })
    except managerException as exp:
        return genError(str(exp))


@webApi.route(os.path.join(ApiPath, 'version'), methods = ['GET'])
def getVersion() -> Response:
    logging.debug('API get version -> %s' + Version)
    return jsonResponse({
        'success': True,
        'version': Version,
    })


def startServer() -> None:
    logging.warning('API server at http://:%i%s' % (ApiPort, ApiPath))
    logging.warning('API ' + ('without token' if ApiToken == '' else 'token -> %s' % ApiToken))
    pywsgi.WSGIServer(('0.0.0.0', ApiPort), webApi).serve_forever()  # powered by gevent
