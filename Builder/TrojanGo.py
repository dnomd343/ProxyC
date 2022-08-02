#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json


def sslConfig(proxyInfo: dict) -> dict:
    return {
        'verify': proxyInfo['verify'],
        **({} if proxyInfo['sni'] == '' else {
            'sni': proxyInfo['sni']
        }),
        **({} if proxyInfo['alpn'] is None else {
            'alpn': proxyInfo['alpn'].split(',')
        }),
    }


def wsConfig(proxyInfo: dict) -> dict:
    if proxyInfo['ws'] is None:
        return {'enabled': False}
    wsObject = {
        'enabled': True,
        'path': proxyInfo['ws']['path']
    }
    if proxyInfo['ws']['host'] != '':
        wsObject['host'] = proxyInfo['ws']['host']
    return wsObject


def ssConfig(proxyInfo: dict) -> dict:
    return {
        'enabled': False if proxyInfo['ss'] is None else True,
        **({} if proxyInfo['ss'] is None else {
            'method': proxyInfo['ss']['method'],
            'password': proxyInfo['ss']['passwd'],
        })
    }


def pluginConfig(proxyInfo: dict) -> dict:
    return {
        'enabled': False if proxyInfo['plugin'] is None else True,
        **({} if proxyInfo['plugin'] is None else {
            'type': 'shadowsocks',
            'command': proxyInfo['plugin']['type'],
            'option': proxyInfo['plugin']['param'],
        })
    }


def load(proxyInfo: dict, socksInfo: dict, configFile: str) -> tuple[list, str, dict]:
    trojanGoConfig = {
        'run_type': 'client',
        'local_addr': socksInfo['addr'],
        'local_port': socksInfo['port'],
        'remote_addr': proxyInfo['server'],
        'remote_port': proxyInfo['port'],
        'password': [
            proxyInfo['passwd']
        ],
        'log_level': 0,  # 0 -> debug level
        'ssl': sslConfig(proxyInfo),
        'websocket': wsConfig(proxyInfo),
        'shadowsocks': ssConfig(proxyInfo),
        'transport_plugin': pluginConfig(proxyInfo),
    }
    return ['trojan-go', '-config', configFile], json.dumps(trojanGoConfig), {}  # command, fileContent, envVar
