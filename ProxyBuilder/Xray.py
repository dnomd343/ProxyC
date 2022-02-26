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

def xrayStreamConfig(streamInfo: dict) -> dict: # 生成xray传输方式配置
    streamType = streamInfo['type']
    if streamType == 'tcp':
        return V2ray.tcpConfig(streamInfo, __secureConfig)
    elif streamType == 'kcp':
        return V2ray.kcpConfig(streamInfo, __secureConfig)
    elif streamType == 'ws':
        return V2ray.wsConfig(streamInfo, True, __secureConfig)
    elif streamType == 'h2':
        return V2ray.h2Config(streamInfo, __secureConfig)
    elif streamType == 'quic':
        return V2ray.quicConfig(streamInfo, __secureConfig)
    elif streamType == 'grpc':
        return V2ray.grpcConfig(streamInfo, __secureConfig)
    else:
        raise Exception('Unknown stream type')
