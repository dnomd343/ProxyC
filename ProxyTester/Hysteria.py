#!/usr/bin/python
# -*- coding:utf-8 -*-

import copy
import json

testConfig = {}

hysteriaProtocolList = [
    'udp',
    'wechat-video',
    'faketcp',
]


def __hysteriaConfig(protocol: str, isObfs: bool, isAuth: bool) -> dict:
    caption = 'Hysteria protocol ' + protocol
    proxyInfo = {
        'type': 'hysteria',
        'server': testConfig['addr'],
        'port': testConfig['port'],
        'protocol': protocol,
        'sni': testConfig['host']
    }
    serverConfig = {
        'listen': testConfig['bind'] + ':' + str(testConfig['port']),
        'protocol': protocol,
        'cert': testConfig['cert'],
        'key': testConfig['key'],
    }

    if isObfs:
        caption += ' (with obfs)'
        proxyInfo['obfs'] = testConfig['passwd']
        serverConfig['obfs'] = testConfig['passwd']
    if isAuth:
        caption += ' (with auth)'
        proxyInfo['auth'] = testConfig['passwd']
        serverConfig['auth'] = {
            'mode': 'passwords',
            'config': [testConfig['passwd']]
        }

    return {
        'caption': caption,
        'proxy': proxyInfo,
        'server': {
            'startCommand': ['hysteria', '-c', testConfig['file'], 'server'],
            'fileContent': json.dumps(serverConfig),
            'filePath': testConfig['file'],
            'envVar': {}
        },
        'aider': None
    }


def test(config: dict) -> list:
    global testConfig
    testConfig = copy.deepcopy(config)
    if testConfig['bind'].find(':') >= 0:
        testConfig['bind'] = '[' + testConfig['bind'] + ']'

    testList = []
    for protocol in hysteriaProtocolList:
        testList.append(__hysteriaConfig(protocol, False, False))
        testList.append(__hysteriaConfig(protocol, False, True))
        testList.append(__hysteriaConfig(protocol, True, False))
        testList.append(__hysteriaConfig(protocol, True, True))
    return testList
