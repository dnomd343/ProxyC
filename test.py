#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import requests
from Builder import Shadowsocks
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Methods import ssMethods
from Basis.Functions import getAvailablePort

ssPassword = ''

def loadConfig(serverPort: int, method: str) -> dict:  # load basic config option
    config = {
        'server': '127.0.0.1',
        'server_port': serverPort,  # type -> int
        'method': method,
        'password': ssPassword,
    }
    return config


def ssRust(serverPort: int, method: str) -> tuple[dict, list]:
    config = loadConfig(serverPort, method)
    return config, ['ss-rust-server', '-v']


def ssLibev(serverPort: int, method: str) -> tuple[dict, list]:
    config = loadConfig(serverPort, method)
    return config, ['ss-libev-server', '-v']


def ssPython(serverPort: int, method: str) -> tuple[dict, list]:
    config = loadConfig(serverPort, method)
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
    if config['method'] in ['idea-cfb', 'seed-cfb']:  # Only older versions of openssl are supported
        config['extra_opts'] = '--libopenssl=libcrypto.so.1.0.0'
    config['shadowsocks'] = 'ss-python-server'
    return config, ['ss-bootstrap-server', '--debug', '-vv']


def ssPythonLegacy(serverPort: int, method: str) -> tuple[dict, list]:
    config = loadConfig(serverPort, method)
    config['shadowsocks'] = 'ss-python-legacy-server'
    return config, ['ss-bootstrap-server', '--debug', '-vv']


def loadTest(serverType: str, clientType: str, method: str, timeout: float) -> None:
    logging.warning('Shadowsocks test -> server = %s | client = %s | method = %s' % (serverType, clientType, method))
    global ssPassword
    if method.startswith('2022-blake3-'):
        ssPassword = 'ZG5vbWQzNDNkbm9tZDM0M2Rub21kMzQzZG5vbWQzNDM='  # base64 encode of 'dnomd343' * 4
        if method == '2022-blake3-aes-128-gcm':
            ssPassword = 'ZG5vbWQzNDNkbm9tZDM0Mw=='  # base64 encode of 'dnomd343' * 2
    else:
        ssPassword = 'dnomd343'
    title = '%s_%s_%s' % (serverType, clientType, method)
    workDir = '/tmp/ProxyC'
    serverPort = getAvailablePort()
    socksPort = getAvailablePort()
    proxyInfo = {
        'server': '127.0.0.1',
        'port': serverPort,
        'method': method,
        'passwd': ssPassword,
        'plugin': None
    }
    socksInfo = {
        'addr': '127.0.0.1',
        'port': socksPort
    }
    ssClientLoad = {
        'ss-rust': Shadowsocks.ssRust,
        'ss-libev': Shadowsocks.ssLibev,
        'ss-python': Shadowsocks.ssPython,
        'ss-python-legacy': Shadowsocks.ssPythonLegacy
    }[clientType]
    ssConfig, ssClient = ssClientLoad(proxyInfo, socksInfo, isUdp = False)
    client = Process(workDir, cmd = ssClient + ['-c', os.path.join(workDir, title + '_client.json')], file = {
        'path': os.path.join(workDir, title + '_client.json'),
        'content': json.dumps(ssConfig)
    }, isStart = False)

    ssServerLoad = {
        'ss-rust': ssRust,
        'ss-libev': ssLibev,
        'ss-python': ssPython,
        'ss-python-legacy': ssPythonLegacy
    }[serverType]
    ssConfig, ssServer = ssServerLoad(serverPort, method)
    server = Process(workDir, cmd = ssServer + ['-c', os.path.join(workDir, title + '_server.json')], file = {
        'path': os.path.join(workDir, title + '_server.json'),
        'content': json.dumps(ssConfig)
    }, isStart = False)

    client.start()
    server.start()
    time.sleep(timeout)
    errFlag = False
    try:
        request = requests.get(
            'http://baidu.com',
            proxies = {
                'http': 'socks5://127.0.0.1:%i' % socksPort,
                'https': 'socks5://127.0.0.1:%i' % socksPort
            },
            timeout = 10
        )
        request.raise_for_status()
        logging.info('socks5 127.0.0.1:%i -> ok' % socksPort)
    except Exception as exp:
        logging.error('socks5 127.0.0.1:%i -> error' % socksPort)
        logging.error('requests exception\n' + str(exp))
        errFlag = True
    client.quit()
    server.quit()
    if errFlag:
        logging.error('client capture output\n' + str(client.output))
        logging.error('server capture output\n' + str(server.output))


def test_1() -> None:
    for ssType in ssMethods:
        for method in ssMethods[ssType]:
            timeout = 0.1
            if 'python' in ssType: timeout = 0.3
            if 'python-legacy' in ssType:
                timeout = 0.8
                if method == 'table' or method == 'salsa20-ctr': timeout = 2
            loadTest(ssType, ssType, method, timeout)


def test_2() -> None:
    for ssServer in ssMethods:
        for method in ssMethods[ssServer]:
            for ssClient in ssMethods:
                if method not in ssMethods[ssClient]: continue
                timeout = 0.1
                if 'python' in ssServer or 'python' in ssClient: timeout = 0.3
                if method == 'table': timeout = 0.8
                if 'python-legacy' in ssServer or 'python-legacy' in ssClient: timeout = 1
                if method == 'salsa20-ctr': timeout = 3
                loadTest(ssServer, ssClient, method, timeout)


test_1()
# test_2()
# loadTest('ss-python-legacy', 'ss-python-legacy', 'salsa20-ctr', 3)
