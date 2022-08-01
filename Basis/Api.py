#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from gevent import pywsgi
from Basis.Logger import logging
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
    logging.critical('get task list')
    return jsonResponse({})


@webApi.route('/task', methods = ['POST'])
def createTask() -> Response:
    if not tokenCheck():  # token check
        return tokenError()
    logging.critical('create task')
    return jsonResponse({})


@webApi.route('/task/<taskId>', methods = ['GET'])
def getTaskInfo() -> Response:
    if not tokenCheck():  # token check
        return tokenError()
    logging.critical('get task info')
    return jsonResponse({})


@webApi.route('/version', methods = ['GET'])
def getVersion() -> Response:
    logging.debug('get version -> %s' + Version)
    return jsonResponse({
        'version': Version
    })


def startServer(apiPort: int = 7839, apiToken: str = '') -> None:
    global token
    token = apiToken
    logging.warning('API server at http://:%i/' % apiPort)
    logging.warning('API ' + ('without token' if apiToken == '' else 'token -> %s' % apiToken))
    pywsgi.WSGIServer(('0.0.0.0', apiPort), webApi).serve_forever()  # powered by gevent
