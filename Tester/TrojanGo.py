#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from Tester import Plugin
from Builder import TrojanGo
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Functions import md5Sum
from Basis.Functions import genFlag
from Basis.Methods import trojanGoMethods
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


# def wsConfig(proxyInfo: dict) -> dict:
#     if proxyInfo['ws'] is None:
#         return {'enabled': False}
#     wsObject = {
#         'enabled': True,
#         'path': proxyInfo['ws']['path']
#     }
#     if proxyInfo['ws']['host'] != '':
#         wsObject['host'] = proxyInfo['ws']['host']
#     return wsObject
#
#
# def ssConfig(proxyInfo: dict) -> dict:
#     return {**{
#         'enabled': False if proxyInfo['ss'] is None else True
#     }, **({} if proxyInfo['ss'] is None else {
#         'method': proxyInfo['ss']['method'],
#         'password': proxyInfo['ss']['passwd'],
#     })}
#
#
# def pluginConfig(proxyInfo: dict) -> dict:
#     return {**{
#         'enabled': False if proxyInfo['plugin'] is None else True
#     }, **({} if proxyInfo['plugin'] is None else {
#         'type': 'shadowsocks',
#         'command': proxyInfo['plugin']['type'],
#         'option': proxyInfo['plugin']['param'],
#     })}


def loadServer(configFile: str, proxyInfo: dict) -> Process:
    trojanGoConfig = {
        'run_type': 'server',
        'local_addr': proxyInfo['server'],
        'local_port': proxyInfo['port'],
        'remote_addr': '127.0.0.1',  # remote address are only for shadowsocks fallback (pointless here)
        'remote_port': getAvailablePort(),  # random port (will not be used)
        'password': [
            proxyInfo['passwd']
        ],
        'disable_http_check': True,
        'ssl': {
            'cert': settings['cert'],
            'key': settings['key']
        },
        'websocket': TrojanGo.wsConfig(proxyInfo),
        'shadowsocks': TrojanGo.ssConfig(proxyInfo),
        'transport_plugin': TrojanGo.pluginConfig(proxyInfo),
    }
    serverFile = os.path.join(settings['workDir'], configFile)
    return Process(settings['workDir'], cmd = ['trojan-go', '-config', serverFile], file = {
        'path': serverFile,
        'content': json.dumps(trojanGoConfig)
    }, isStart = False)


def loadClient(configFile: str, proxyInfo: dict, socksInfo: dict) -> Process:  # load client process
    clientFile = os.path.join(settings['workDir'], configFile)
    trojanGoCommand, trojanGoConfig, _ = TrojanGo.load(proxyInfo, socksInfo, clientFile)
    return Process(settings['workDir'], cmd = trojanGoCommand, file = {
        'path': clientFile,
        'content': trojanGoConfig
    }, isStart = False)


def loadTest(wsObject: dict or None, ssObject: dict or None, plugin: dict or None = None) -> dict:
    proxyInfo = {  # connection info
        'server': settings['serverBind'],
        'port': getAvailablePort(),
        'passwd': genFlag(length = 8),  # random password
        'sni': settings['host'],
        'alpn': None,
        'verify': True,
        'ws': wsObject,
        'ss': ssObject,
    }
    socksInfo = {  # socks5 interface for test
        'addr': settings['clientBind'],
        'port': getAvailablePort()
    }
    configName = 'trojan-go%s%s%s' % (
        ('' if wsObject is None else '_ws'),
        ('' if ssObject is None else '_' + ssObject['method']),
        ('' if plugin is None else '_' + md5Sum(plugin['type'] + plugin['caption'])[:8])
    )
    pluginClient = {'plugin': None if plugin is None else plugin['client']}
    pluginServer = {'plugin': None if plugin is None else plugin['server']}
    testInfo = {  # release test info
        'title': 'Trojan-Go test: original' + \
                 ('' if ssObject is None else ' (with %s encrypt)' % ssObject['method']) + \
                 ('' if wsObject is None else ' (with websocket)') + \
                 ('' if plugin is None else ' [%s -> %s]' % (plugin['type'], plugin['caption'])),
        'client': loadClient(configName + '_client.json', {**proxyInfo, **pluginClient}, socksInfo),
        'server': loadServer(configName + '_server.json', {**proxyInfo, **pluginServer}),
        'socks': socksInfo,  # exposed socks5 address
        'interface': {
            'addr': proxyInfo['server'],
            'port': proxyInfo['port'],
        }
    }
    if plugin is not None:
        testInfo['server'] = plugin['inject'](testInfo['server'], plugin)
    logging.debug('New trojan-go test -> %s' % testInfo)
    return testInfo


def load():
    pluginTest = []
    pluginIter = Plugin.load('trojan-go')
    while True:
        try:
            pluginTest.append(next(pluginIter))  # export data of plugin generator
        except StopIteration:
            break
    wsObject = {
        'host': settings['host'],
        'path': '/' + genFlag(length = 6),
    }
    yield loadTest(None, None, None)
    for method in [''] + trojanGoMethods:  # different encryption for trojan-go
        ssObject = {
            'method': method,
            'passwd': genFlag(length = 8)
        }
        yield loadTest(wsObject, None if ssObject['method'] == '' else ssObject, None)
    for plugin in pluginTest:  # different plugin for trojan-go
        yield loadTest(None, None, plugin)
