#!/usr/bin/python
# -*- coding:utf-8 -*-

import copy
import ProxyTester.Plugin as sip003

testConfig = {}

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

sip003PluginList = [ # SIP003插件列表
    'obfs-local',
    'simple-tls',
    'v2ray-plugin',
    'xray-plugin',
    'kcptun-client',
    'gost-plugin',
    'ck-client',
    'gq-client',
    'mtt-client',
    'rabbit-plugin',
    'qtun-client',
    'gun-plugin'
]


def __ssServerConfig(method: str, plugin: str or None) -> list:
    rabbitPort = 20191
    proxyInfo = {
        'type': 'ss',
        'server': testConfig['addr'],
        'port': testConfig['port'],
        'passwd': testConfig['passwd'],
        'method': method
    }
    caption = 'Shadowsocks method ' + method
    if method in ['plain', 'none']: # plain / none -> ss-rust
        serverCommand = [
            'ss-rust-server',
            '-s', testConfig['bind'] + ':' + str(testConfig['port']),
            '-k', testConfig['passwd'],
            '-m', method
        ]
    elif method == 'salsa20-ctr': # salsa20-ctr -> ss-python-legacy
        serverCommand = [
            'ss-bootstrap-server', '--no-udp',
            '--shadowsocks', 'ss-python-legacy-server',
            '-s', testConfig['bind'],
            '-p', str(testConfig['port']),
            '-k', testConfig['passwd'],
            '-m', method
        ]
    else: # others -> ss-python
        mbedtlsMethods = [
            'aes-128-cfb128',
            'aes-192-cfb128',
            'aes-256-cfb128',
            'camellia-128-cfb128',
            'camellia-192-cfb128',
            'camellia-256-cfb128',
        ]
        if method in mbedtlsMethods:
            method = 'mbedtls:' + method
        serverCommand = [
            'ss-bootstrap-server', '--no-udp',
            '--shadowsocks', 'ss-python-server',
            '-s', testConfig['bind'],
            '-p', str(testConfig['port']),
            '-k', testConfig['passwd'],
            '-m', method
        ]
        if method == 'idea-cfb' or method == 'seed-cfb':
            serverCommand.append('--libopenssl=libcrypto.so.1.0.0')

    if plugin is None: # 无插件模式
        return [{
                'caption': caption,
                'proxy': proxyInfo,
                'server': {
                    'startCommand': serverCommand,
                    'fileContent': None,
                    'filePath': None,
                    'envVar': {}
                },
                'aider': None
        }]

    if plugin == 'rabbit-plugin': # rabbit-tcp
        proxyInfo['port'] = rabbitPort
        proxyInfo['plugin'] = {
            'type': 'rabbit-plugin',
            'param': 'serviceAddr=127.0.0.1:' + str(testConfig['port']) + ';password=' + testConfig['passwd']
        }
        return [{
            'proxy': proxyInfo,
            'caption': 'Shadowsocks plugin rabbit-plugin (basic mode)',
            'server': {
                'startCommand': serverCommand,
                'fileContent': None,
                'filePath': None,
                'envVar': {}
            },
            'aider': {
                'startCommand': [
                    'rabbit',
                    '-mode', 's',
                    '-password', testConfig['passwd'],
                    '-rabbit-addr', ':' + str(rabbitPort)
                ],
                'fileContent': None,
                'filePath': None,
                'envVar': {}
            }
        }]

    # others plugin
    result = []
    pluginConfig = sip003.loadPluginConfig( # 载入插件配置
        plugin, testConfig['host'], testConfig['cert'], testConfig['key']
    )
    serverBaseCommand = copy.deepcopy(serverCommand)
    for pluginOption in pluginConfig:
        serverCommand = copy.deepcopy(serverBaseCommand)
        serverCommand.append('--plugin')
        serverCommand.append(pluginOption['server']['type'])
        serverCommand.append('--plugin-opts')
        serverCommand.append(pluginOption['server']['param'])
        proxyInfo['plugin'] = pluginOption['client']
        result.append(copy.deepcopy({
            'proxy': proxyInfo,
            'caption': 'Shadowsocks plugin ' + proxyInfo['plugin']['type'] + ' (' + pluginOption['caption'] + ')',
            'server': {
                'startCommand': serverCommand,
                'fileContent': pluginOption['file'],
                'filePath': pluginOption['path'],
                'envVar': {}
            },
            'aider': None
        }))
    return result


def test(config: dict) -> list:
    global testConfig
    testConfig = config

    testList = []
    for method in ssMethodList: # all Shadowsocks methods
        testList += __ssServerConfig(method, None)
    for plugin in sip003PluginList: # all SIP003 plugin
        testList += __ssServerConfig('aes-256-ctr', plugin)
    return testList
