#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import itertools
from Builder import Brook
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Functions import genFlag
from Basis.Functions import hostFormat
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


def originStream(isUot: bool) -> dict:
    return {
        'caption': 'original' + (' (UDP over TCP)' if isUot else ''),
        'info': {
            'type': 'origin',
            'uot': isUot,
        },
        'command': lambda proxyInfo: ['server'] + [  # callback function for loading brook command
            '--listen', '%s:%i' % (hostFormat(proxyInfo['server'], v6Bracket = True), proxyInfo['port']),
            '--password', proxyInfo['passwd'],
        ]
    }


def loadWsCommand(proxyInfo: dict) -> list:  # load start command for brook server
    return ([
        'wsserver', '--listen', '%s:%i' % (hostFormat(proxyInfo['server'], v6Bracket = True), proxyInfo['port'])
    ] if proxyInfo['stream']['secure'] is None else [
        'wssserver', '--domainaddress', '%s:%i' % (proxyInfo['stream']['host'], proxyInfo['port'])
    ]) + [
        '--path', proxyInfo['stream']['path'],
        '--password', proxyInfo['passwd'],
    ] + ([] if proxyInfo['stream']['secure'] is None else [
        '--cert', settings['cert'],
        '--certkey', settings['key'],
    ]) + (['--withoutBrookProtocol'] if proxyInfo['stream']['raw'] else [])


def wsStream(isRaw: bool, isSecure: bool):
    return {
        'caption': 'websocket' + (' (with tls)' if isSecure else '') + (' (without brook)' if isRaw else ''),
        'info': {
            'type': 'ws',
            'host': settings['host'],
            'path': '/' + genFlag(length = 6),
            'raw': isRaw,
            'secure': {'verify': True} if isSecure else None,
        },
        'command': loadWsCommand  # callback function for loading brook command
    }


def loadTest(stream: dict) -> dict:
    proxyInfo = {
        'server': settings['serverBind'],
        'port': getAvailablePort(),
        'passwd': genFlag(),
        'stream': stream['info']
    }
    socksInfo = {  # socks5 interface for test
        'addr': settings['clientBind'],
        'port': getAvailablePort()
    }
    clientCommand, _, _ = Brook.load(proxyInfo, socksInfo, '')
    serverCommand = ['brook', '--debug', '--listen', ':'] + stream['command'](proxyInfo)
    testInfo = {  # release test info
        'title': 'Brook test: ' + stream['caption'],
        'client': Process(settings['workDir'], cmd = clientCommand, isStart = False),
        'server': Process(settings['workDir'], cmd = serverCommand, isStart = False),
        'socks': socksInfo,  # exposed socks5 address
        'interface': {
            'addr': proxyInfo['server'],
            'port': proxyInfo['port'],
        }
    }
    logging.debug('New brook test -> %s' % testInfo)
    return testInfo


def load():
    streams = []
    addStream = lambda x: streams.append(copy.deepcopy(x))
    for isUot in [False, True]:
        addStream(originStream(isUot))  # origin stream test
    for isSecure, isRaw in itertools.product([False, True], [False, True]):
        addStream(wsStream(isRaw, isSecure))  # websocket stream test
    for stream in streams:
        yield loadTest(stream)
