#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from gevent import pywsgi
from Basis.Logger import logging
from Basis.Manager import Manager
from Basis.Constant import Version
from flask import Flask, Response, request

token = ''
webPath = '/'  # root of api server
webApi = Flask(__name__)  # init flask server


def jsonResponse(data: dict) -> Response:  # return json mime
    return Response(json.dumps(data), mimetype = 'application/json')


def tokenError() -> Response:
    return jsonResponse({
        'success': False,
        'message': 'Invalid token'
    })


def tokenCheck() -> bool:
    if token == '': return True  # without token check
    if request.method == 'GET':
        return request.args.get('token') == token
    elif request.method == 'POST':
        return request.json.get('token') == token
    else:
        return False  # polyfill


@webApi.route('/task', methods = ['GET'])
def getTaskList() -> Response:
    if not tokenCheck():  # token check
        return tokenError()
    try:
        taskList = Manager.listUnion()
        logging.debug('api get task list -> %s' % taskList)
        return jsonResponse({
            'success': True,
            'task': taskList,
        })
    except:
        return jsonResponse({
            'success': False,
            'message': 'Unknown error'
        })


@webApi.route('/task', methods = ['POST'])
def createTask() -> Response:
    if not tokenCheck():  # token check
        return tokenError()
    checkList = request.json.get('check')
    proxyList = request.json.get('proxy')
    if checkList is None or type(checkList) != list:
        return jsonResponse({
            'success': False,
            'message': 'invalid check list',
        })
    if proxyList is None or type(proxyList) != list:
        return jsonResponse({
            'success': False,
            'message': 'invalid proxy list',
        })
    logging.debug('api create task -> check: %s | proxy: %s' % (checkList, proxyList))

    # TODO: format check and proxy list

    tasks = []
    for proxy in proxyList:
        tasks.append({**proxy, 'check': checkList})
    checkId = Manager.addUnion(tasks)
    logging.debug('api return check id %s' % checkId)

    return jsonResponse({
        'success': True,
        'id': checkId,
        'check': checkList,
        'proxy': proxyList,
    })


@webApi.route('/task/<taskId>', methods = ['GET'])
def getTaskInfo(taskId: str) -> Response:
    if not tokenCheck():  # token check
        return tokenError()
    logging.critical('API get task %s info' % taskId)
    if not Manager.isUnion(taskId):
        return jsonResponse({
            'success': False,
            'message': 'task id not found',
        })
    return jsonResponse({
        'success': True,
        **Manager.getUnion(taskId)
    })


@webApi.route('/version', methods = ['GET'])
def getVersion() -> Response:
    logging.debug('get version -> %s' + Version)
    return jsonResponse({
        'success': True,
        'version': Version,
    })


def startServer(apiToken: str = '', apiPort: int = 7839) -> None:
    global token
    token = apiToken
    logging.warning('API server at http://:%i/' % apiPort)
    logging.warning('API ' + ('without token' if apiToken == '' else 'token -> %s' % apiToken))
    pywsgi.WSGIServer(('0.0.0.0', apiPort), webApi).serve_forever()  # powered by gevent
