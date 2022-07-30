#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from Builder import ShadowsocksR
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Functions import genFlag, getAvailablePort
from Basis.Methods import ssrMethods, ssrProtocols, ssrObfuscations

settings = {
    'serverBind': '127.0.0.1',
    'clientBind': '127.0.0.1',
    # 'serverBind': '::1',
    # 'clientBind': '::1',
    'workDir': '/tmp/ProxyC'
}


def loadServer(configFile: str, proxyInfo: dict) -> Process:  # load server process
    ssrConfig = {
        'server': proxyInfo['server'],
        'server_port': proxyInfo['port'],  # type -> int
        'password': proxyInfo['passwd'],
        'method': proxyInfo['method'],
        'protocol': proxyInfo['protocol'],
        'protocol_param': proxyInfo['protocolParam'],
        'obfs': proxyInfo['obfs'],
        'obfs_param': proxyInfo['obfsParam']
    }
    serverFile = os.path.join(settings['workDir'], configFile)
    return Process(settings['workDir'], cmd = ['ssr-server', '-vv', '-c', serverFile], file = {
        'path': serverFile,
        'content': json.dumps(ssrConfig)
    }, isStart = False)


def loadClient(configFile: str, proxyInfo: dict, socksInfo: dict) -> Process:  # load client process
    clientFile = os.path.join(settings['workDir'], configFile)
    ssrCommand, ssrConfig, _ = ShadowsocksR.load(proxyInfo, socksInfo, clientFile)
    return Process(settings['workDir'], cmd = ssrCommand, file = {
        'path': clientFile,
        'content': ssrConfig
    }, isStart = False)


def loadTest(method: str, protocol: str, obfs: str) -> dict:
    proxyInfo = {  # connection info
        'server': settings['serverBind'],
        'port': getAvailablePort(),
        'passwd': genFlag(length = 8),  # random password
        'method': method,
        'protocol': protocol,
        'protocolParam': '',
        'obfs': obfs,
        'obfsParam': '',
    }
    socksInfo = {  # socks5 interface for test
        'addr': settings['clientBind'],
        'port': getAvailablePort()
    }
    configName = '%s_%s_%s' % (method, protocol, obfs)  # prefix of config file name
    testInfo = {  # release test info
        'title': 'ShadowsocksR test: method = %s | protocol = %s | obfs = %s' % (method, protocol, obfs),
        'client': loadClient(configName + '_client.json', proxyInfo, socksInfo),
        'server': loadServer(configName + '_server.json', proxyInfo),
        'socks': socksInfo,  # exposed socks5 address
        'interface': {
            'addr': proxyInfo['server'],
            'port': proxyInfo['port']
        }
    }
    logging.debug('New shadowsocksr test -> %s' % testInfo)
    return testInfo


def load():
    for method in ssrMethods:
        yield loadTest(method, 'origin', 'plain')
    for protocol in ssrProtocols:
        yield loadTest('aes-128-ctr', protocol, 'plain')
    for obfs in ssrObfuscations:
        yield loadTest('aes-128-ctr', 'origin', obfs)
