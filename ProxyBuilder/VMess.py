#!/usr/bin/python
# -*- coding:utf-8 -*-

import json

logLevel = 'warning'

def __baseConfig(socksPort: int, outboundObject: dict) -> dict:
    return {
        'log': {
            'loglevel': logLevel
        },
        'inbounds': [
            {
                'port': socksPort,
                'listen': '127.0.0.1',
                'protocol': 'socks',
                'settings': {
                    'udp': True,
                    'auth': 'noauth'
                }
            }
        ],
        'outbounds': [
            outboundObject
        ]
    }

def __vmessConfig(proxyInfo: dict) -> dict:
    streamObject = {}
    return {
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
        'streamSettings': streamObject
    }

def load(proxyInfo: dict, socksPort: int, configFile: str) -> tuple[list or None, str or None, dict or None]:
    """
    VMess配置载入
        proxyInfo: 节点信息
        socksPort: 本地通讯端口
        configFile: 配置文件路径

        节点有误:
            return None, None, None

        载入成功:
            return startCommand, fileContent, envVar
    """

    config = __baseConfig(socksPort, __vmessConfig(proxyInfo))

    return ['v2ray', '-c', configFile], json.dumps(config), {}

info = {
    'server': '1.1.1.1',
    'port': 12345,
    'method': 'aes-128-gcm',
    'id': 'eb6273f1-a98f-59f6-ba52-945f11dee100',
    'aid': 64,
    'stream': {
        'type': 'tcp',
        'obfs': None,
        'secure': {
            'sni': '',
            'alpn': 'h2,http/1.1',
            'verify': True
        }
    }
}

ret = load(info, 1080, '/tmp/ProxyC/test.json')
print(ret)
