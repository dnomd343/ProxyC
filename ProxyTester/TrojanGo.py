#!/usr/bin/python
# -*- coding:utf-8 -*-

import copy
import json

from ProxyTester import Plugin

config = {}

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
        'local_addr': '127.0.0.1',
        'local_port': config['port'],
        'remote_addr': '127.0.0.1', # only for shadowsocks fallback
        'remote_port': 343,
        'password': [
            config['passwd']
        ],
        'disable_http_check': True,
        'ssl': {
            'cert': config['cert'],
            'key': config['key']
        }
    }
    proxyInfo = {
        'type': 'trojan-go',
        'server': '127.0.0.1',
        'port': config['port'],
        'passwd': config['passwd'],
        'sni': config['host'],
    }
    if ssMethod is not None: # add Shadowsocks encrypt
        caption += ' ' + ssMethod + ' encrypt'
        serverConfig['shadowsocks'] = {
            'enabled': True,
            'method': ssMethod,
            'password': config['passwd']
        }
        proxyInfo['ss'] = {
            'method': ssMethod,
            'passwd': config['passwd']
        }
    if isWs: # add WebSocket config
        caption += ' (websocket)'
        serverConfig['websocket'] = {
            'enabled': True,
            'host': config['host'],
            'path': config['path']
        }
        proxyInfo['ws'] = {
            'host': config['host'],
            'path': config['path']
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
            'param': 'serviceAddr=127.0.0.1:' + str(config['port']) + ';password=' + config['passwd']
        }
        trojanBaseConfig['server']['transport_plugin'] = {
            'enabled': True,
            'type': 'other',
            'command': 'rabbit',
            'arg': [
                '-mode', 's',
                '-password', config['passwd'],
                '-rabbit-addr', ':' + str(rabbitPort)
            ]
        }
        trojanBaseConfig['file'] = None
        trojanBaseConfig['path'] = None
        return [trojanBaseConfig]

    # other plugin
    pluginConfig = Plugin.loadPluginConfig(plugin, config['host'], config['cert'], config['key'])  # 载入插件配置
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
                'startCommand': ['trojan-go', '-config', config['file']],
                'fileContent': json.dumps(trojanGoConfig['server']),
                'filePath': config['file'],
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

def trojanGoTest(trojanGoConfig: dict) -> list:
    result = []
    for key, value in trojanGoConfig.items(): # trojanGoConfig -> config
        config[key] = value

    result += loadTrojanGoConfig([loadTrojanGo(False, None)]) # basic test
    result += loadTrojanGoConfig([loadTrojanGo(True, None)])
    for ssMethod in trojanGoMethod:
        result += loadTrojanGoConfig([loadTrojanGo(False, ssMethod)]) # basic test with shadowsocks
        result += loadTrojanGoConfig([loadTrojanGo(True, ssMethod)])

    for plugin in sip003PluginList: # plugin test -> cause zombie process (imperfect trojan-go)
        result += loadTrojanGoConfig(loadTrojanGoPlugin(plugin))

    return result
