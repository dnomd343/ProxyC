#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
from ProxyBuilder import Xray

def load(proxyInfo: dict, socksPort: int, configFile: str) -> tuple[list, str, dict]:
    """
    VLESS配置载入
        proxyInfo: 节点信息
        socksPort: 本地通讯端口
        configFile: 配置文件路径

            return startCommand, fileContent, envVar
    """
    user = {
        'id': proxyInfo['id'],
        'encryption': proxyInfo['method']
    }
    if proxyInfo['stream']['secure'] is not None and proxyInfo['stream']['secure']['type'] == 'xtls':
        flowType = proxyInfo['stream']['secure']['flow']
        if flowType == 'xtls-origin':
            user['flow'] = 'xtls-rprx-origin'
        elif flowType == 'xtls-direct':
            user['flow'] = 'xtls-rprx-direct'
        elif flowType == 'xtls-splice':
            user['flow'] = 'xtls-rprx-splice'
        else:
            raise Exception('Unknown XTLS flow')
        if proxyInfo['stream']['secure']['udp443']:
            user['flow'] += '-udp443'
    outboundConfig = {
        'protocol': 'vless',
        'settings': {
            'vnext': [
                {
                    'address': proxyInfo['server'],
                    'port': proxyInfo['port'],
                    'users': [user]
                }
            ]
        },
        'streamSettings': Xray.xrayStreamConfig(proxyInfo['stream'])
    }
    config = Xray.baseConfig(socksPort, outboundConfig) # VLESS节点配置
    return ['xray', '-c', configFile], json.dumps(config), {}
