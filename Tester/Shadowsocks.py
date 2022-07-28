#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import base64
import itertools
from Builder import Shadowsocks
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Methods import ssMethods, ssAllMethods
from Basis.Functions import genFlag, getAvailablePort

settings = {
    'serverBind': '127.0.0.1',
    'clientBind': '127.0.0.1',  # aka socks5 address
    'workDir': '/tmp/ProxyC'
}


def loadConfig(proxyInfo: dict) -> dict:  # load basic config option
    config = {
        'server': proxyInfo['server'],
        'server_port': proxyInfo['port'],  # type -> int
        'method': proxyInfo['method'],
        'password': proxyInfo['passwd'],
    }
    if proxyInfo['plugin'] is not None:  # with plugin
        config['plugin'] = proxyInfo['plugin']['type']
        config['plugin_opts'] = proxyInfo['plugin']['param']
    return config


def pluginUdp(plugin: str, pluginParam: str) -> bool:  # whether the plugin uses UDP
    if plugin in ['obfs-local', 'simple-tls', 'ck-client', 'gq-client', 'mtt-client', 'rabbit-plugin']:
        return False  # UDP is not used
    if plugin in ['v2ray-plugin', 'xray-plugin', 'gost-plugin']:
        if 'mode=quic' not in pluginParam.split(';'):  # non-quic mode does not use UDP
            return False
    return True  # UDP is assumed by default


def ssRust(proxyInfo: dict, isUdp: bool) -> tuple[dict, list]:
    config = loadConfig(proxyInfo)
    if isUdp:  # proxy UDP traffic
        config['mode'] = 'tcp_and_udp'
    return config, ['ss-rust-server', '-v']


def ssLibev(proxyInfo: dict, isUdp: bool) -> tuple[dict, list]:
    config = loadConfig(proxyInfo)
    if isUdp:  # proxy UDP traffic
        config['mode'] = 'tcp_and_udp'
    return config, ['ss-libev-server', '-v']


def ssPython(proxyInfo: dict, isUdp: bool) -> tuple[dict, list]:
    config = loadConfig(proxyInfo)
    mbedtlsMethods = [
        'aes-128-cfb128',
        'aes-192-cfb128',
        'aes-256-cfb128',
        'camellia-128-cfb128',
        'camellia-192-cfb128',
        'camellia-256-cfb128',
    ]
    if config['method'] in mbedtlsMethods:  # mbedtls methods should use prefix `mbedtls:`
        config['method'] = 'mbedtls:' + config['method']
    if config['method'] in ['idea-cfb', 'seed-cfb']:  # only older versions of openssl are supported
        config['extra_opts'] = '--libopenssl=libcrypto.so.1.0.0'
    if not isUdp:
        config['no_udp'] = True  # UDP traffic is not proxied
    config['shadowsocks'] = 'ss-python-server'
    return config, ['ss-bootstrap-server', '--debug', '-vv']


def ssPythonLegacy(proxyInfo: dict, isUdp: bool) -> tuple[dict, list]:
    config = loadConfig(proxyInfo)
    if not isUdp:
        config['no_udp'] = True  # UDP traffic is not proxied
    config['shadowsocks'] = 'ss-python-legacy-server'
    return config, ['ss-bootstrap-server', '--debug', '-vv']


def loadPassword(method: str) -> str:
    b64 = lambda x: base64.b64encode(x.encode(encoding = 'utf-8')).decode(encoding = 'utf-8')  # base64 encode
    if not method.startswith('2022-blake3-'):  # normal method
        return genFlag(length = 8)
    if method == '2022-blake3-aes-128-gcm':  # 2022-blake3-aes-128-gcm use 16 byte length password
        return b64(genFlag(length = 16))
    return b64(genFlag(length = 32))  # three other 2022-blake3-* methods use 32 byte length password


def loadClient(ssType: str, configFile: str, proxyInfo: dict, socksInfo: dict) -> Process:
    ssConfig, ssClient = {  # generate client start command and its config file
        'ss-rust': Shadowsocks.ssRust,
        'ss-libev': Shadowsocks.ssLibev,
        'ss-python': Shadowsocks.ssPython,
        'ss-python-legacy': Shadowsocks.ssPythonLegacy
    }[ssType](proxyInfo, socksInfo, isUdp = False)
    clientFile = os.path.join(settings['workDir'], configFile)
    return Process(settings['workDir'], cmd = ssClient + ['-c', clientFile], file = {  # load client process
        'path': clientFile,
        'content': json.dumps(ssConfig)
    }, isStart = False)


def loadServer(ssType: str, configFile: str, proxyInfo: dict) -> Process:
    ssConfig, ssServer = {  # generate server start command and its config file
        'ss-rust': ssRust,
        'ss-libev': ssLibev,
        'ss-python': ssPython,
        'ss-python-legacy': ssPythonLegacy
    }[ssType](proxyInfo, isUdp = False)
    serverFile = os.path.join(settings['workDir'], configFile)
    return Process(settings['workDir'], cmd = ssServer + ['-c', serverFile], file = {  # load server process
        'path': serverFile,
        'content': json.dumps(ssConfig)
    }, isStart = False)


def loadTest(serverType: str, clientType: str, method: str) -> dict:
    proxyInfo = {  # connection info
        'server': settings['serverBind'],
        'port': getAvailablePort(),
        'method': method,
        'passwd': loadPassword(method),
        'plugin': None
    }
    socksInfo = {  # socks5 interface for test
        'addr': settings['clientBind'],
        'port': getAvailablePort()
    }
    configName = '%s_%s_%s' % (serverType, clientType, method)  # prefix of config file name
    testInfo = {  # release test info
        'title': 'Shadowsocks test: {%s <- %s -> %s}' % (serverType, method, clientType),
        'client': loadClient(clientType, configName + '_client.json', proxyInfo, socksInfo),
        'server': loadServer(serverType, configName + '_server.json', proxyInfo),
        'socks': socksInfo,  # exposed socks5 address
        'interface': {
            'addr': proxyInfo['server'],
            'port': proxyInfo['port']
        }
    }
    logging.debug('New shadowsocks test -> %s' % testInfo)
    return testInfo


def load(isExtra: bool = False):
    if not isExtra:  # just test basic connection
        for method in ssAllMethods:  # test every method for once
            for ssType in ssMethods:  # found the client which support this method
                if method not in ssMethods[ssType]: continue
                yield loadTest(ssType, ssType, method)  # ssType <-- method --> ssType
                break  # don't need other client
        return
    for ssServer in ssMethods:  # traverse all shadowsocks type as server
        for method, ssClient in itertools.product(ssMethods[ssServer], ssMethods):  # supported methods and clients
            if method not in ssMethods[ssClient]: continue
            yield loadTest(ssServer, ssClient, method)  # ssServer <-- method --> ssClient
