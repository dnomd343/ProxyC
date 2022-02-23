#!/usr/bin/python
# -*- coding:utf-8 -*-

import json

logLevel = 'warning'

def __baseConfig(socksPort: int, outboundObject: dict) -> dict: # v2ray配置生成
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

def __secureConfig(secureInfo: dict or None) -> dict: # TLS加密传输配置
    if secureInfo is None:
        return {}
    return {
        'security': 'tls',
        'tlsSettings': {
            'allowInsecure': not secureInfo['verify']
            # sni
            # alpn
        }
    }

def __tcpConfig(streamInfo: dict) -> dict: # TCP传输方式配置
    tcpObject = {}
    return {**{
        'network': 'tcp',
        'tcpSettings': tcpObject
    }, **__secureConfig(streamInfo['secure'])}

def __kcpConfig(streamInfo: dict) -> dict: # mKCP传输方式配置
    kcpObject = {}
    return {**{
        'network': 'kcp',
        'kcpSettings': kcpObject
    }, **__secureConfig(streamInfo['secure'])}

def __wsConfig(streamInfo: dict) -> dict: # WebSocket传输方式配置
    wsObject = {}
    return {**{
        'network': 'ws',
        'wsSettings': wsObject
    }, **__secureConfig(streamInfo['secure'])}

def __h2Config(streamInfo: dict) -> dict: # HTTP/2传输方式配置
    h2Object = {}
    return {**{
        'network': 'h2',
        'httpSettings': h2Object
    }, **__secureConfig(streamInfo['secure'])}

def __quicConfig(streamInfo: dict) -> dict: # QUIC传输方式配置
    quicObject = {}
    return {**{
        'network': 'quic',
        'quicSettings': quicObject
    }, **__secureConfig(streamInfo['secure'])}

def __grpcConfig(streamInfo: dict) -> dict: # gRPC传输方式配置
    grpcObject = {}
    return {**{
        'network': 'grpc',
        'grpcSettings': grpcObject
    }, **__secureConfig(streamInfo['secure'])}

def __vmessConfig(proxyInfo: dict) -> dict: # VMess节点配置
    streamType = proxyInfo['stream']['type']
    if streamType == 'tcp':
        streamObject = __tcpConfig(proxyInfo['stream'])
    elif streamType == 'kcp':
        streamObject = __kcpConfig(proxyInfo['stream'])
    elif streamType == 'ws':
        streamObject = __wsConfig(proxyInfo['stream'])
    elif streamType == 'h2':
        streamObject = __h2Config(proxyInfo['stream'])
    elif streamType == 'quic':
        streamObject = __quicConfig(proxyInfo['stream'])
    elif streamType == 'grpc':
        streamObject = __grpcConfig(proxyInfo['stream'])
    else:
        raise Exception('Unknown stream type')
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
print(ret[1])
