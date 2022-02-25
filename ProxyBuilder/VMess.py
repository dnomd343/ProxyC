#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
from ProxyBuilder import V2ray

def load(proxyInfo: dict, socksPort: int, configFile: str) -> tuple[list, str, dict]:
    """
    VMess配置载入
        proxyInfo: 节点信息
        socksPort: 本地通讯端口
        configFile: 配置文件路径

            return startCommand, fileContent, envVar
    """
    outboundConfig = {
        'protocol': 'vmess',
        'settings': {
            'vnext': [
                {
                    'address': proxyInfo['server'],
                    'port': proxyInfo['port'],
                    'users': [
                        {
                            'id': proxyInfo['id'],
                            'alterId': proxyInfo['aid'],
                            'security': proxyInfo['method']
                        }
                    ]
                }
            ]
        },
        'streamSettings': V2ray.v2rayStreamConfig(proxyInfo['stream'])
    }
    config = V2ray.baseConfig(socksPort, outboundConfig) # VMess节点配置
    return ['v2ray', '-c', configFile], json.dumps(config), {}
