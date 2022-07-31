#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from Tester import Plugin
from Tester import Settings
from Builder import TrojanGo
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Functions import md5Sum
from Basis.Functions import genFlag
from Basis.Methods import trojanGoMethods
from Basis.Functions import getAvailablePort


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
            'cert': Settings['cert'],
            'key': Settings['key']
        },
        'websocket': TrojanGo.wsConfig(proxyInfo),
        'shadowsocks': TrojanGo.ssConfig(proxyInfo),
        'transport_plugin': TrojanGo.pluginConfig(proxyInfo),
    }
    serverFile = os.path.join(Settings['workDir'], configFile)
    return Process(Settings['workDir'], cmd = ['trojan-go', '-config', serverFile], file = {
        'path': serverFile,
        'content': json.dumps(trojanGoConfig)
    }, isStart = False)


def loadClient(configFile: str, proxyInfo: dict, socksInfo: dict) -> Process:  # load client process
    clientFile = os.path.join(Settings['workDir'], configFile)
    trojanGoCommand, trojanGoConfig, _ = TrojanGo.load(proxyInfo, socksInfo, clientFile)
    return Process(Settings['workDir'], cmd = trojanGoCommand, file = {
        'path': clientFile,
        'content': trojanGoConfig
    }, isStart = False)


def loadTest(wsObject: dict or None, ssObject: dict or None, plugin: dict or None = None) -> dict:
    proxyInfo = {  # connection info
        'server': Settings['serverBind'],
        'port': getAvailablePort(),
        'passwd': genFlag(length = 8),  # random password
        'sni': Settings['host'],
        'alpn': None,
        'verify': True,
        'ws': wsObject,
        'ss': ssObject,
    }
    socksInfo = {  # socks5 interface for test
        'addr': Settings['clientBind'],
        'port': getAvailablePort()
    }
    configName = 'trojan-go%s%s%s' % (
        ('' if wsObject is None else '_ws'),
        ('' if ssObject is None else '_' + ssObject['method']),
        ('' if plugin is None else '_' + md5Sum(plugin['type'] + plugin['caption'])[:8])
    )
    pluginClient = {'plugin': None if plugin is None else plugin['client']}
    pluginServer = {'plugin': None if plugin is None else plugin['server']}
    testTitle = 'Trojan-Go test: original' + \
        ('' if ssObject is None else ' (with %s encrypt)' % ssObject['method']) + \
        ('' if wsObject is None else ' (with websocket)') + \
        ('' if plugin is None else ' [%s -> %s]' % (plugin['type'], plugin['caption']))
    testInfo = {  # release test info
        'title': testTitle,
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
        'host': Settings['host'],
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
