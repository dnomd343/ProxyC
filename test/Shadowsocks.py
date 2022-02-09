#!/usr/bin/python
# -*- coding:utf-8 -*-

ssMethodList = [
    'aes-128-gcm',
    'aes-192-gcm',
    'aes-256-gcm',
    'aes-128-ctr',
    'aes-192-ctr',
    'aes-256-ctr',
    'aes-128-ocb',
    'aes-192-ocb',
    'aes-256-ocb',
    'aes-128-ofb',
    'aes-192-ofb',
    'aes-256-ofb',
    'aes-128-cfb',
    'aes-192-cfb',
    'aes-256-cfb',
    'aes-128-cfb1',
    'aes-192-cfb1',
    'aes-256-cfb1',
    'aes-128-cfb8',
    'aes-192-cfb8',
    'aes-256-cfb8',
    'aes-128-cfb128',
    'aes-192-cfb128',
    'aes-256-cfb128',
    'camellia-128-cfb',
    'camellia-192-cfb',
    'camellia-256-cfb',
    'camellia-128-cfb128',
    'camellia-192-cfb128',
    'camellia-256-cfb128',
    'plain',
    'none',
    'table',
    'rc4',
    'rc4-md5',
    'rc2-cfb',
    'bf-cfb',
    'cast5-cfb',
    'des-cfb',
    'idea-cfb',
    'seed-cfb',
    'salsa20',
    'salsa20-ctr',
    'xchacha20',
    'chacha20',
    'chacha20-ietf',
    'chacha20-poly1305',
    'chacha20-ietf-poly1305',
    'xchacha20-ietf-poly1305'
]

def test(port, password):
    testList = []
    for method in ssMethodList:
        proxyInfo = {
            'type': 'ss',
            'server': '127.0.0.1',
            'port': int(port),
            'password': password,
            'method': method,
            'plugin': '',
            'pluginArg': '',
        }
        testInfo = 'Shadowsocks method ' + method
        if method == 'plain' or method == 'none':
            serverCommand = [
                'ss-rust-server', '-U',
                '-s', '0.0.0.0:' + str(port),
                '-k', password,
                '-m', method
            ]
        elif method == 'salsa20-ctr':
            serverCommand = [
                'ss-bootstrap-server',
                '--shadowsocks', 'ss-python-legacy-server',
                '-p', str(port),
                '-k', password,
                '-m', method
            ]
        else:
            specialMethods = [
                'aes-128-cfb128',
                'aes-192-cfb128',
                'aes-256-cfb128',
                'camellia-128-cfb128',
                'camellia-192-cfb128',
                'camellia-256-cfb128',
            ]
            if method in specialMethods:
                method = 'mbedtls:' + method
            serverCommand = [
                'ss-bootstrap-server',
                '--shadowsocks', 'ss-python-server',
                '-p', str(port),
                '-k', password,
                '-m', method
            ]
            if method == 'idea-cfb' or method == 'seed-cfb':
                serverCommand.append('--libopenssl=libcrypto.so.1.0.0')
        testList.append({
            'caption': testInfo,
            'proxyInfo': proxyInfo,
            'serverCommand': serverCommand
        })
    return testList
