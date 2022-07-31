#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import itertools
from Tester import V2ray
from Builder import VMess
from Tester import Settings
from Builder import pathEnv
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Functions import md5Sum
from Basis.Functions import genUUID
from Basis.Methods import vmessMethods
from Basis.Functions import getAvailablePort


def loadServer(configFile: str, proxyInfo: dict, streamConfig: dict) -> Process:  # load server process
    vmessConfig = V2ray.loadConfig({
        'protocol': 'vmess',
        'listen': proxyInfo['server'],
        'port': proxyInfo['port'],
        'settings': {
            'clients': [{  # server will auto adapt the method
                'id': proxyInfo['id'],
                'alterId': proxyInfo['aid'],
            }]
        },
        'streamSettings': streamConfig
    })
    serverFile = os.path.join(Settings['workDir'], configFile)
    return Process(Settings['workDir'], cmd = ['v2ray', '-c', serverFile], file = {
        'path': serverFile,
        'content': json.dumps(vmessConfig)
    }, env= {
        'PATH': pathEnv,
        'v2ray.vmess.aead.forced': 'false'  # enable non-aead test (aid not 0)
    }, isStart = False)


def loadClient(configFile: str, proxyInfo: dict, socksInfo: dict) -> Process:  # load client process
    clientFile = os.path.join(Settings['workDir'], configFile)
    vmessCommand, vmessConfig, _ = VMess.load(proxyInfo, socksInfo, clientFile)
    return Process(Settings['workDir'], cmd = vmessCommand, file = {
        'path': clientFile,
        'content': vmessConfig
    }, isStart = False)


def loadTest(method: str, aid: int, stream: dict) -> dict:
    proxyInfo = {  # connection info
        'server': Settings['serverBind'],
        'port': getAvailablePort(),
        'method': method,
        'id': genUUID(),  # random uuid v5
        'aid': aid,
        'stream': stream['info']
    }
    socksInfo = {  # socks5 interface for test
        'addr': Settings['clientBind'],
        'port': getAvailablePort()
    }
    configName = 'vmess_%s_%i_%s' % (method, aid, md5Sum(stream['caption'])[:8])
    testInfo = {  # release test info
        'title': 'VMess test: %s [security = %s | alterId = %i]' % (stream['caption'], method, aid),
        'client': loadClient(configName + '_client.json', proxyInfo, socksInfo),
        'server': loadServer(configName + '_server.json', proxyInfo, stream['server']),
        'socks': socksInfo,  # exposed socks5 address
        'interface': {
            'addr': proxyInfo['server'],
            'port': proxyInfo['port'],
        }
    }
    logging.debug('New vmess test -> %s' % testInfo)
    return testInfo


def load():
    streams = V2ray.loadStream()  # load v2ray-core stream list
    for method, aid in itertools.product(vmessMethods, [0, 64]):  # test every methods (and whether enable aead)
        yield loadTest(method, aid, streams[0])
    for stream in streams[1:]:  # skip first stream that has benn checked
        yield loadTest('auto', 0, stream)  # aead with auto security
