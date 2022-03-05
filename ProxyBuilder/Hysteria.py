#!/usr/bin/python
# -*- coding:utf-8 -*-

import copy
import json

defaultUpSpeed = 10000
defaultDownSpeed = 10000

def load(proxyInfo: dict, socksPort: int, configFile: str) -> tuple[list, str or None, dict]:
    """
    Hysteria配置载入
        proxyInfo: 节点信息
        socksPort: 本地通讯端口
        configFile: 配置文件路径

            return startCommand, fileContent, envVar
    """
    proxyInfo = copy.deepcopy(proxyInfo)
    if proxyInfo['server'].find(':') >= 0:
        proxyInfo['server'] = '[' + proxyInfo['server'] + ']' # IPv6

    config = {
        'server': proxyInfo['server'] + ':' + str(proxyInfo['port']),
        'protocol': proxyInfo['protocol'],
        'up_mbps': defaultUpSpeed,
        'down_mbps': defaultDownSpeed,
        'socks5': {
            'listen': '127.0.0.1:' + str(socksPort)
        }
    }

    if proxyInfo['obfs'] is not None:
        config['obfs'] = proxyInfo['obfs']
    if proxyInfo['auth'] is not None:
        config['auth_str'] = proxyInfo['auth']
    if proxyInfo['sni'] != '':
        config['server_name'] = proxyInfo['sni']
    if proxyInfo['alpn'] is not None:
        config['alpn'] = proxyInfo['alpn']
    if not proxyInfo['verify']:
        config['insecure'] = True

    return ['hysteria', '-c', configFile, 'client'], json.dumps(config), {}
