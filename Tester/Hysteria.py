#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import itertools
from Builder import Hysteria
from Basis.Test import Settings
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Constant import hysteriaProtocols
from Basis.Functions import hostFormat, genFlag, getAvailablePort


def loadServer(configFile: str, hysteriaConfig: dict) -> Process:
    serverFile = os.path.join(Settings['workDir'], configFile)
    return Process(Settings['workDir'], cmd = ['hysteria', '-c', serverFile, 'server'], file = {
        'path': serverFile,
        'content': json.dumps(hysteriaConfig)
    }, isStart = False)


def loadClient(configFile: str, proxyInfo: dict, socksInfo: dict) -> Process:
    clientFile = os.path.join(Settings['workDir'], configFile)
    hysteriaCommand, hysteriaConfig, _ = Hysteria.load(proxyInfo, socksInfo, clientFile)
    return Process(Settings['workDir'], cmd = hysteriaCommand, file = {
        'path': clientFile,
        'content': hysteriaConfig
    }, isStart = False)


def loadTest(protocol: str, isObfs: bool, isAuth: bool) -> dict:
    proxyInfo = {
        'type': 'hysteria',
        'server': Settings['serverBind'],
        'port': getAvailablePort(),
        'protocol': protocol,
        'obfs': None,
        'passwd': None,
        'up': 10,
        'down': 50,
        'sni': Settings['host'],
        'alpn': None,
        'verify': True,
    }
    socksInfo = {  # socks5 interface for test
        'addr': Settings['clientBind'],
        'port': getAvailablePort()
    }
    serverConfig = {
        'listen': '%s:%i' % (hostFormat(proxyInfo['server'], v6Bracket = True), proxyInfo['port']),
        'protocol': proxyInfo['protocol'],
        'cert': Settings['cert'],
        'key': Settings['key'],
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
        'caption': caption,
        'client': loadClient(configName + '_client.json', proxyInfo, socksInfo),
        'server': loadServer(configName + '_server.json', serverConfig),
        'socks': socksInfo,  # exposed socks5 address
        'interface': {
            'addr': proxyInfo['server'],
            'port': proxyInfo['port'],
        }
    }
    logging.debug('New Hysteria test -> %s' % testInfo)
    return testInfo


def load():
    for protocol, isObfs, isAuth in itertools.product(hysteriaProtocols, [False, True], [False, True]):
        yield loadTest(protocol, isObfs, isAuth)
    logging.info('Hysteria test yield complete')
