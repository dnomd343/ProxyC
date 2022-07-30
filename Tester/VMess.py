#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import itertools
from Tester import V2ray
from Builder import VMess
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Functions import md5Sum
from Basis.Functions import genUUID
from Basis.Functions import getAvailablePort

from Builder import pathEnv
from Basis.Methods import vmessMethods

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
    serverFile = os.path.join(settings['workDir'], configFile)
    return Process(settings['workDir'], cmd = ['v2ray', '-c', serverFile], file = {
        'path': serverFile,
        'content': json.dumps(vmessConfig)
    }, env= {
        'PATH': pathEnv,
        'v2ray.vmess.aead.forced': 'false'  # enable non-aead test (aid not 0)
    }, isStart = False)


def loadClient(configFile: str, proxyInfo: dict, socksInfo: dict) -> Process:  # load client process
    clientFile = os.path.join(settings['workDir'], configFile)
    vmessCommand, vmessConfig, _ = VMess.load(proxyInfo, socksInfo, clientFile)
    return Process(settings['workDir'], cmd = vmessCommand, file = {
        'path': clientFile,
        'content': vmessConfig
    }, isStart = False)


def loadTest(method: str, aid: int, stream: dict) -> dict:
    proxyInfo = {  # connection info
        'server': settings['serverBind'],
        'port': getAvailablePort(),
        'method': 'auto',
        'id': genUUID(),  # random uuid v5
        'aid': aid,
        'stream': stream['info']
    }
    socksInfo = {  # socks5 interface for test
        'addr': settings['clientBind'],
        'port': getAvailablePort()
    }
    configName = 'vmess_%s_%i_%s' % (method, aid, md5Sum(stream['caption'])[:8])
    testInfo = {  # release test info
        'title': 'VMess test: security = %s | alterId = %i [%s]' % (method, aid, stream['caption']),
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
    stream = {
        'caption': 'TCP stream (with tls)',
        'info': {
            'type': 'tcp',
            'obfs': None,
            'secure': {
                'sni': settings['host'],
                'alpn': None,
                'verify': True,
            },
        },
        'server': {
            'network': 'tcp',
            'tcpSettings': {},
            'security': 'tls',
            'tlsSettings': {
                'alpn': ['h2', 'http/1.1'],
                'certificates': [{
                    'certificateFile': settings['cert'],
                    'keyFile': settings['key'],
                }]
            }
        }
    }

    # for method, aid in itertools.product(vmessMethods, [0, 64]):
    #     yield loadTest(method, aid, stream)
    for stream in V2ray.loadStream():
        yield loadTest('auto', 0, stream)
