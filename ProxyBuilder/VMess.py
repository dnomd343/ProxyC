#!/usr/bin/python
# -*- coding:utf-8 -*-

import json

logLevel = 'warning'

httpHeader = {
    'type': 'http',
    'request': {
        'version': '1.1',
        'method': 'GET',
        'path': [],
        'headers': {
            'Host': [],
            'User-Agent': [
                'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_2 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/53.0.2785.109 Mobile/14A456 Safari/601.1.46'
            ],
            'Accept-Encoding': [
                'gzip, deflate'
            ],
            'Connection': [
                'keep-alive'
            ],
            'Pragma': 'no-cache'
        }
    }
}

kcpSettings = {
    'mtu': 1350,
    'tti': 50,
    'uplinkCapacity': 12,
    'downlinkCapacity': 100,
    'congestion': False,
    'readBufferSize': 2,
    'writeBufferSize': 2,
    'header': {}
}

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
    tlsObject = {
        'allowInsecure': not secureInfo['verify'],
        'alpn': secureInfo['alpn'].split(',')
    }
    if secureInfo['sni'] != '':
        tlsObject['serverName'] = secureInfo['sni']
    return {
        'security': 'tls',
        'tlsSettings': tlsObject
    }

def __tcpConfig(streamInfo: dict) -> dict: # TCP传输方式配置
    tcpObject = {}
    if streamInfo['obfs'] is not None:
        httpHeader['request']['path'].append(streamInfo['obfs']['path'])
        httpHeader['request']['headers']['Host'] = streamInfo['obfs']['host'].split(',')
        tcpObject['header'] = httpHeader
    return {**{
        'network': 'tcp',
        'tcpSettings': tcpObject
    }, **__secureConfig(streamInfo['secure'])}

def __kcpConfig(streamInfo: dict) -> dict: # mKCP传输方式配置
    kcpObject = kcpSettings
    kcpObject['header']['type'] = streamInfo['obfs']
    if streamInfo['seed'] is not None:
        kcpObject['seed'] = streamInfo['seed']
    return {**{
        'network': 'kcp',
        'kcpSettings': kcpObject
    }, **__secureConfig(streamInfo['secure'])}

def __wsConfig(streamInfo: dict) -> dict: # WebSocket传输方式配置
    wsObject = {}
    if streamInfo['path'] != '':
        wsObject['path'] = streamInfo['path']
    if streamInfo['host'] != '':
        wsObject['headers'] = {}
        wsObject['headers']['Host'] = streamInfo['host']
    if streamInfo['ed'] is not None:
        wsObject['maxEarlyData'] = streamInfo['ed']
        wsObject['earlyDataHeaderName'] = 'Sec-WebSocket-Protocol'
    return {**{
        'network': 'ws',
        'wsSettings': wsObject
    }, **__secureConfig(streamInfo['secure'])}

def __h2Config(streamInfo: dict) -> dict: # HTTP/2传输方式配置
    h2Object = {
        'path': streamInfo['path']
    }
    if streamInfo['host'] != '':
        h2Object['host'] = streamInfo['host'].split(',')
    return {**{
        'network': 'h2',
        'httpSettings': h2Object
    }, **__secureConfig(streamInfo['secure'])}

def __quicConfig(streamInfo: dict) -> dict: # QUIC传输方式配置
    return {**{
        'network': 'quic',
        'quicSettings': {
            'security': streamInfo['method'],
            'key': streamInfo['passwd'],
            'header': {
                'type': streamInfo['obfs']
            }
        }
    }, **__secureConfig(streamInfo['secure'])}

def __grpcConfig(streamInfo: dict) -> dict: # gRPC传输方式配置
    return {**{
        'network': 'grpc',
        'grpcSettings': {
            'serviceName': streamInfo['service']
        }
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
    try:
        config = __baseConfig(socksPort, __vmessConfig(proxyInfo))
        return ['v2ray', '-c', configFile], json.dumps(config), {}
    except:
        return None, None, None
