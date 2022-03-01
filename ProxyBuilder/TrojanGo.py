#!/usr/bin/python
# -*- coding:utf-8 -*-

import json

def __tlsConfig(proxyInfo: dict) -> dict:
    tlsConfig = {
        'verify': proxyInfo['verify']
    }
    if proxyInfo['sni'] != '':
        tlsConfig['sni'] = proxyInfo['sni']
    if proxyInfo['alpn'] is not None:
        tlsConfig['alpn'] = proxyInfo['alpn'].split(',')
    return tlsConfig

def __wsConfig(proxyInfo: dict) -> dict:
    if proxyInfo['ws'] is None:
        return {
            'enabled': False
        }
    wsConfig = {
        'enabled': True,
        'path': proxyInfo['ws']['path']
    }
    if proxyInfo['ws']['host'] != '':
        wsConfig['host'] = proxyInfo['ws']['host']
    return wsConfig

def __ssConfig(proxyInfo: dict) -> dict:
    if proxyInfo['ss'] is None:
        return {
            'enabled': False
        }
    return {
        'enabled': True,
        'method': proxyInfo['ss']['method'],
        'password': proxyInfo['ss']['passwd']
    }

def __pluginConfig(proxyInfo: dict) -> dict:
    if proxyInfo['plugin'] is None:
        return {
            'enabled': False
        }
    return {
        'enabled': True,
        'type': 'shadowsocks',
        'command': proxyInfo['plugin']['type'],
        'option': proxyInfo['plugin']['param']
    }

def load(proxyInfo: dict, socksPort: int, configFile: str) -> tuple[list, str, dict]:
    """
    Trojan-Go配置载入
        proxyInfo: 节点信息
        socksPort: 本地通讯端口
        configFile: 配置文件路径

            return startCommand, fileContent, envVar
    """
    config = {
        'run_type': 'client',
        'local_addr': '127.0.0.1',
        'local_port': socksPort,
        'remote_addr': proxyInfo['server'],
        'remote_port': proxyInfo['port'],
        'password': [
            proxyInfo['passwd']
        ],
        'log_level': 0,
        'ssl': __tlsConfig(proxyInfo),
        'websocket': __wsConfig(proxyInfo),
        'shadowsocks': __ssConfig(proxyInfo),
        'transport_plugin': __pluginConfig(proxyInfo)
    }
    return ['trojan-go', '-config', configFile], json.dumps(config), {'PATH': '/usr/bin'}
