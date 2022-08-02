#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import itertools
from Builder import Brook
from Basis.Logger import logging
from Basis.Process import Process
from Tester.Settings import Settings
from Basis.Functions import hostFormat, genFlag, getAvailablePort


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
    brookCommand = [
        'wsserver', '--listen', '%s:%i' % (hostFormat(proxyInfo['server'], v6Bracket = True), proxyInfo['port'])
    ] if proxyInfo['stream']['secure'] is None else [
        'wssserver', '--domainaddress', '%s:%i' % (proxyInfo['stream']['host'], proxyInfo['port'])
    ]
    brookCommand += [
        '--path', proxyInfo['stream']['path'],
        '--password', proxyInfo['passwd'],
    ]
    brookCommand += ([] if proxyInfo['stream']['secure'] is None else [
        '--cert', Settings['cert'],
        '--certkey', Settings['key'],
    ])
    return brookCommand + (['--withoutBrookProtocol'] if proxyInfo['stream']['raw'] else [])


def wsStream(isRaw: bool, isSecure: bool):
    return {
        'caption': 'websocket' + (' (with tls)' if isSecure else '') + (' (without brook)' if isRaw else ''),
        'info': {
            'type': 'ws',
            'host': Settings['host'],
            'path': '/' + genFlag(length = 6),
            'raw': isRaw,
            'secure': {'verify': True} if isSecure else None,
        },
        'command': loadWsCommand  # callback function for loading brook command
    }


def loadTest(stream: dict) -> dict:
    proxyInfo = {
        'server': Settings['serverBind'],
        'port': getAvailablePort(),
        'passwd': genFlag(),
        'stream': stream['info']
    }
    socksInfo = {  # socks5 interface for test
        'addr': Settings['clientBind'],
        'port': getAvailablePort()
    }
    clientCommand, _, _ = Brook.load(proxyInfo, socksInfo, '')
    serverCommand = ['brook', '--debug', '--listen', ':'] + stream['command'](proxyInfo)
    testInfo = {  # release test info
        'caption': 'Brook test: ' + stream['caption'],
        'client': Process(Settings['workDir'], cmd = clientCommand, isStart = False),
        'server': Process(Settings['workDir'], cmd = serverCommand, isStart = False),
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
