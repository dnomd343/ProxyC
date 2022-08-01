#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from gevent import pywsgi
from Basis.Logger import logging
from Basis.Constant import Version
from flask import Flask, Response, request

webPath = '/'  # root of api server
webApi = Flask(__name__)  # init flask server


def jsonResponse(data: dict) -> Response:
    return Response(json.dumps(data), mimetype = 'application/json')


@webApi.route('/version', methods = ['GET'])
def getVersion() -> Response:
    logging.debug('get version -> %s' + Version)
    return jsonResponse({
        'version': Version
    })


def startServer(apiPort: int = 7839, apiToken: str = '', isWsgi: bool = True) -> None:
    global webApi, webPath
    logging.warning(
        'start api server at http://:%i/' % apiPort + (' (enable WSGI)' if isWsgi else '')
    )
    logging.warning('server ' + ('without token' if apiToken == '' else 'api token -> %s' % apiToken))
    if not isWsgi:
        webApi.run(host = '0.0.0.0', port = apiPort, debug = True, threaded = True)  # ordinary server (for debug)
    else:
        server = pywsgi.WSGIServer(('0.0.0.0', apiPort), webApi)  # powered by gevent
        server.serve_forever()
