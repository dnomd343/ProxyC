#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyBuilder import V2ray

baseConfig = V2ray.baseConfig

def __secureConfig(secureInfo: dict or None) -> dict: # TLS/XTLS加密传输配置
    if secureInfo is None:
        return {}
    secureObject = {
        'allowInsecure': not secureInfo['verify']
    }
    if secureInfo['alpn'] is not None:
        secureObject['alpn'] = secureInfo['alpn'].split(',')
    if secureInfo['sni'] != '':
        secureObject['serverName'] = secureInfo['sni']
    if secureInfo['type'] == 'tls':
        return {
            'security': 'tls',
            'tlsSettings': secureObject
        }
    elif secureInfo['type'] == 'xtls':
        return {
            'security': 'xtls',
            'xtlsSettings': secureObject
        }
    else:
        raise Exception('Unknown secure type')

def wsConfig(streamInfo: dict, secureFunc) -> dict: # WebSocket传输方式配置
    wsObject = {
        'path': streamInfo['path']
    }
    if streamInfo['host'] != '':
        wsObject['headers'] = {}
        wsObject['headers']['Host'] = streamInfo['host']
    if streamInfo['ed'] is not None: # ed参数写入路径 -> /...?ed=xxx
        if wsObject['path'].find('?') == -1: # 原路径不带参数
            wsObject['path'] += '?ed=' + str(streamInfo['ed'])
        else:
            wsObject['path'] += '&ed=' + str(streamInfo['ed'])
    return {**{
        'network': 'ws',
        'wsSettings': wsObject
    }, **secureFunc(streamInfo['secure'])}

def xrayStreamConfig(streamInfo: dict) -> dict: # 生成xray传输方式配置
    streamType = streamInfo['type']
    if streamType == 'tcp':
        return V2ray.tcpConfig(streamInfo, __secureConfig)
    elif streamType == 'kcp':
        return V2ray.kcpConfig(streamInfo, __secureConfig)
    elif streamType == 'ws':
        return wsConfig(streamInfo, __secureConfig)
    elif streamType == 'h2':
        return V2ray.h2Config(streamInfo, __secureConfig)
    elif streamType == 'quic':
        return V2ray.quicConfig(streamInfo, __secureConfig)
    elif streamType == 'grpc':
        return V2ray.grpcConfig(streamInfo, __secureConfig)
    else:
        raise Exception('Unknown stream type')
