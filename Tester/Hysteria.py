#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import itertools
from Builder import Hysteria
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Functions import genFlag
from Basis.Functions import hostFormat
from Basis.Methods import hysteriaProtocols
from Basis.Functions import getAvailablePort

settings = {
    'serverBind': '127.0.0.1',
    'clientBind': '127.0.0.1',
    # 'serverBind': '::1',
    # 'clientBind': '::1',
    'workDir': '/tmp/ProxyC',
    'host': '343.re',
    'cert': '/etc/ssl/certs/343.re/fullchain.pem',
    'key': '/etc/ssl/certs/343.re/privkey.pem',
}


def loadServer(configFile: str, hysteriaConfig: dict) -> Process:
    serverFile = os.path.join(settings['workDir'], configFile)
    return Process(settings['workDir'], cmd = ['hysteria', '-c', serverFile, 'server'], file = {
        'path': serverFile,
        'content': json.dumps(hysteriaConfig)
    }, isStart = False)


def loadClient(configFile: str, proxyInfo: dict, socksInfo: dict) -> Process:
    clientFile = os.path.join(settings['workDir'], configFile)
    hysteriaCommand, hysteriaConfig, _ = Hysteria.load(proxyInfo, socksInfo, clientFile)
    return Process(settings['workDir'], cmd = hysteriaCommand, file = {
        'path': clientFile,
        'content': hysteriaConfig
    }, isStart = False)


def loadTest(protocol: str, isObfs: bool, isAuth: bool) -> dict:
    proxyInfo = {
        'type': 'hysteria',
        'server': settings['serverBind'],
        'port': getAvailablePort(),
        'protocol': protocol,
        'obfs': None,
        'passwd': None,
        'up': 10,
        'down': 50,
        'sni': settings['host'],
        'alpn': None,
        'verify': True,
    }
    socksInfo = {  # socks5 interface for test
        'addr': settings['clientBind'],
        'port': getAvailablePort()
    }
    serverConfig = {
        'listen': '%s:%i' % (hostFormat(proxyInfo['server'], v6Bracket = True), proxyInfo['port']),
        'protocol': proxyInfo['protocol'],
        'cert': settings['cert'],
        'key': settings['key'],
    }
    configName = 'hysteria_' + protocol
    caption = 'Hysteria protocol ' + protocol
    if isObfs:
        configName += '_obfs'
        caption += ' (with obfs)'
        proxyInfo['obfs'] = genFlag(length = 8)
        serverConfig['obfs'] = proxyInfo['obfs']
    if isAuth:
        configName += '_auth'
        caption += ' (with auth)'
        proxyInfo['passwd'] = genFlag(length = 8)
        serverConfig['auth'] = {
            'mode': 'passwords',
            'config': [proxyInfo['passwd']]
        }
    testInfo = {
        'title': caption,
        'client': loadClient(configName + '_client.json', proxyInfo, socksInfo),
        'server': loadServer(configName + '_server.json', serverConfig),
        'socks': socksInfo,  # exposed socks5 address
        'interface': {
            'addr': proxyInfo['server'],
            'port': proxyInfo['port'],
        }
    }
    logging.debug('New hysteria test -> %s' % testInfo)
    return testInfo


def load():
    for protocol, isObfs, isAuth in itertools.product(hysteriaProtocols, [False, True], [False, True]):
        yield loadTest(protocol, isObfs, isAuth)
