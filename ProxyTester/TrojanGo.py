#!/usr/bin/python
# -*- coding:utf-8 -*-

import copy
import json
from ProxyTester import Plugin

testConfig = {}

trojanGoMethod = [
    'AES-128-GCM',
    'AES-256-GCM',
    'CHACHA20-IETF-POLY1305'
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


def loadTrojanGo(isWs: bool, ssMethod: str or None) -> dict:
    caption = 'Trojan-Go original'
    serverConfig = {
        'run_type': 'server',
        'local_addr': testConfig['bind'],
        'local_port': testConfig['port'],
        'remote_addr': '127.0.0.1', # only for shadowsocks fallback
        'remote_port': 343,
        'password': [
            testConfig['passwd']
        ],
        'disable_http_check': True,
        'ssl': {
            'cert': testConfig['cert'],
            'key': testConfig['key']
        }
    }
    proxyInfo = {
        'type': 'trojan-go',
        'server': testConfig['addr'],
        'port': testConfig['port'],
        'passwd': testConfig['passwd'],
        'sni': testConfig['host'],
    }
    if ssMethod is not None: # add Shadowsocks encrypt
        caption += ' ' + ssMethod + ' encrypt'
        serverConfig['shadowsocks'] = {
            'enabled': True,
            'method': ssMethod,
            'password': testConfig['passwd']
        }
        proxyInfo['ss'] = {
            'method': ssMethod,
            'passwd': testConfig['passwd']
        }
    if isWs: # add WebSocket config
        caption += ' (websocket)'
        serverConfig['websocket'] = {
            'enabled': True,
            'host': testConfig['host'],
            'path': testConfig['path']
        }
        proxyInfo['ws'] = {
            'host': testConfig['host'],
            'path': testConfig['path']
        }
    return {
        'caption': caption,
        'client': proxyInfo,
        'server': serverConfig,
        'file': None,
        'path': None
    }


def loadTrojanGoPlugin(plugin: str) -> list:
    result = []
    rabbitPort = 20191
    trojanBaseConfig = loadTrojanGo(False, None)

    if plugin == 'rabbit-plugin': # rabbit-tcp
        trojanBaseConfig['caption'] = 'Trojan-Go rabbit-plugin (basic mode)'
        trojanBaseConfig['client']['port'] = rabbitPort
        trojanBaseConfig['client']['plugin'] = {
            'type': 'rabbit-plugin',
            'param': 'serviceAddr=127.0.0.1:' + str(testConfig['port']) + ';password=' + testConfig['passwd']
        }
        trojanBaseConfig['server']['transport_plugin'] = {
            'enabled': True,
            'type': 'other',
            'command': 'rabbit',
            'arg': [
                '-mode', 's',
                '-password', testConfig['passwd'],
                '-rabbit-addr', ':' + str(rabbitPort)
            ]
        }
        trojanBaseConfig['file'] = None
        trojanBaseConfig['path'] = None
        return [trojanBaseConfig]

    # other plugin
    pluginConfig = Plugin.loadPluginConfig(plugin, testConfig['host'], testConfig['cert'], testConfig['key'])  # 载入插件配置
    if plugin == 'kcptun-client' and testConfig['bind'].find(':') >= 0:
        trojanBaseConfig['server']['local_addr'] = '[' + trojanBaseConfig['server']['local_addr'] + ']'
    for pluginOption in pluginConfig:
        trojanConfig = copy.deepcopy(trojanBaseConfig)
        trojanConfig['caption'] = 'Trojan-Go plugin ' + plugin + ' (' + pluginOption['caption'] + ')'
        trojanConfig['client']['plugin'] = pluginOption['client']
        trojanConfig['server']['transport_plugin'] = {
            'enabled': True,
            'type': 'shadowsocks',
            'command': pluginOption['server']['type'],
            'option': pluginOption['server']['param']
        }
        trojanConfig['file'] = pluginOption['file']
        trojanConfig['path'] = pluginOption['path']
        result.append(trojanConfig)
    return result


def loadTrojanGoConfig(trojanGoConfigList: list) -> list:
    result = []
    for trojanGoConfig in trojanGoConfigList:
        result.append({
            'caption': trojanGoConfig['caption'],
            'proxy': trojanGoConfig['client'],
            'server': {
                'startCommand': ['trojan-go', '-config', testConfig['file']],
                'fileContent': json.dumps(trojanGoConfig['server']),
                'filePath': testConfig['file'],
                'envVar': {'PATH': '/usr/bin'}
            },
            'aider': {
                'startCommand': None,
                'fileContent': trojanGoConfig['file'],
                'filePath': trojanGoConfig['path'],
                'envVar': {}
            }
        })
    return result


def test(config: dict) -> list:
    global testConfig
    testConfig = config
    testList = []

    testList += loadTrojanGoConfig([loadTrojanGo(False, None)]) # basic test
    testList += loadTrojanGoConfig([loadTrojanGo(True, None)])
    for ssMethod in trojanGoMethod:
        testList += loadTrojanGoConfig([loadTrojanGo(False, ssMethod)]) # basic test with shadowsocks
        testList += loadTrojanGoConfig([loadTrojanGo(True, ssMethod)])

    if config['bind'].find(':') >= 0: # ipv6 format error
        sip003PluginList.remove('gq-client')
        sip003PluginList.remove('rabbit-plugin')
    for plugin in sip003PluginList: # plugin test -> cause zombie process (imperfect trojan-go)
        testList += loadTrojanGoConfig(loadTrojanGoPlugin(plugin))

    return testList
