#!/usr/bin/python
# -*- coding:utf-8 -*-

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

def __secureConfig(secureInfo: dict or None) -> dict: # TLS加密传输配置
    if secureInfo is None:
        return {}
    tlsObject = {
        'allowInsecure': not secureInfo['verify']
    }
    if secureInfo['alpn'] is not None:
        tlsObject['alpn'] = secureInfo['alpn'].split(',')
    if secureInfo['sni'] != '':
        tlsObject['serverName'] = secureInfo['sni']
    return {
        'security': 'tls',
        'tlsSettings': tlsObject
    }

def tcpConfig(streamInfo: dict, secureFunc) -> dict: # TCP传输方式配置
    tcpObject = {}
    if streamInfo['obfs'] is not None:
        httpHeader['request']['path'].append(streamInfo['obfs']['path'])
        httpHeader['request']['headers']['Host'] = streamInfo['obfs']['host'].split(',')
        tcpObject['header'] = httpHeader
    return {**{
        'network': 'tcp',
        'tcpSettings': tcpObject
    }, **secureFunc(streamInfo['secure'])}

def kcpConfig(streamInfo: dict, secureFunc) -> dict: # mKCP传输方式配置
    kcpObject = kcpSettings
    kcpObject['header']['type'] = streamInfo['obfs']
    if streamInfo['seed'] is not None:
        kcpObject['seed'] = streamInfo['seed']
    return {**{
        'network': 'kcp',
        'kcpSettings': kcpObject
    }, **secureFunc(streamInfo['secure'])}

def wsConfig(streamInfo: dict, secureFunc) -> dict: # WebSocket传输方式配置
    wsObject = {
        'path': streamInfo['path']
    }
    if streamInfo['host'] != '':
        wsObject['headers'] = {}
        wsObject['headers']['Host'] = streamInfo['host']
    if streamInfo['ed'] is not None:
        wsObject['maxEarlyData'] = streamInfo['ed']
        wsObject['earlyDataHeaderName'] = 'Sec-WebSocket-Protocol'
    return {**{
        'network': 'ws',
        'wsSettings': wsObject
    }, **secureFunc(streamInfo['secure'])}

def h2Config(streamInfo: dict, secureFunc) -> dict: # HTTP/2传输方式配置
    h2Object = {
        'path': streamInfo['path']
    }
    if streamInfo['host'] != '':
        h2Object['host'] = streamInfo['host'].split(',')
    return {**{
        'network': 'http',
        'httpSettings': h2Object
    }, **secureFunc(streamInfo['secure'])}

def quicConfig(streamInfo: dict, secureFunc) -> dict: # QUIC传输方式配置
    return {**{
        'network': 'quic',
        'quicSettings': {
            'security': streamInfo['method'],
            'key': streamInfo['passwd'],
            'header': {
                'type': streamInfo['obfs']
            }
        }
    }, **secureFunc(streamInfo['secure'])}

def grpcConfig(streamInfo: dict, secureFunc) -> dict: # gRPC传输方式配置
    grpcObject = {
        'serviceName': streamInfo['service']
    }
    if streamInfo['mode'] == 'multi': # gRPC multi-mode not work in v2fly-core
        grpcObject['multiMode'] = True
    return {**{
        'network': 'grpc',
        'grpcSettings': grpcObject
    }, **secureFunc(streamInfo['secure'])}

def v2rayStreamConfig(streamInfo: dict) -> dict: # 生成v2ray传输方式配置
    streamType = streamInfo['type']
    if streamType == 'tcp':
        return tcpConfig(streamInfo, __secureConfig)
    elif streamType == 'kcp':
        return kcpConfig(streamInfo, __secureConfig)
    elif streamType == 'ws':
        return wsConfig(streamInfo, __secureConfig)
    elif streamType == 'h2':
        return h2Config(streamInfo, __secureConfig)
    elif streamType == 'quic':
        return quicConfig(streamInfo, __secureConfig)
    elif streamType == 'grpc':
        return grpcConfig(streamInfo, __secureConfig)
    else:
        raise Exception('Unknown stream type')

def baseConfig(socksPort: int, outboundObject: dict) -> dict: # 基础配置生成
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
