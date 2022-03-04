#!/usr/bin/python
# -*- coding:utf-8 -*-

import copy
from ProxyTester import V2ray

xtlsFlowList = [
    'xtls-origin',
    'xtls-direct',
    'xtls-splice',
]

udpObfsList = V2ray.udpObfsList
quicMethodList = V2ray.quicMethodList

xrayConfig = V2ray.v2rayConfig
loadTcpStream = V2ray.loadTcpStream
loadKcpStream = V2ray.loadKcpStream
loadH2Stream = V2ray.loadH2Stream
loadQuicStream = V2ray.loadQuicStream
loadGrpcStream = V2ray.loadGrpcStream


def loadWsStream(host: str, path: str, isEd: bool) -> dict:
    if not isEd: # without Early-Data
        return {
            'caption': 'WebSocket',
            'client': {
                'type': 'ws',
                'host': host,
                'path': path,
                'secure': None
            },
            'server': {
                'network': 'ws',
                'wsSettings': {
                    'path': path,
                    'headers': {
                        'Host': host
                    }
                }
            }
        }
    return {
        'caption': 'WebSocket Max-Early-Data 2048',
        'client': {
            'type': 'ws',
            'host': host,
            'path': path,
            'ed': 2048,
            'secure': None
        },
        'server': {
            'network': 'ws',
            'wsSettings': {
                'path': path + '?ed=2048',
                'headers': {
                    'Host': host
                }
            }
        }
    }


def addTlsConfig(rawStreamInfo: dict, cert: str, key: str, sni: str) -> dict:
    streamInfo = copy.deepcopy(rawStreamInfo)
    streamInfo['caption'] += ' (tls)'
    streamInfo['client']['secure'] = {
        'type': 'tls',
        'sni': sni
    }
    streamInfo['server']['security'] = 'tls'
    streamInfo['server']['tlsSettings'] = {
        'alpn': [
            'h2',
            'http/1.1'
        ],
        'certificates': [
            {
                'certificateFile': cert,
                'keyFile': key
            }
        ]
    }
    return streamInfo


def addXtlsConfig(rawStreamInfo: dict, cert: str, key: str, sni: str, xtlsFlow: str) -> tuple[str, dict]:
    streamInfo = copy.deepcopy(rawStreamInfo)
    streamInfo['caption'] += ' (' + xtlsFlow + ')'
    streamInfo['client']['secure'] = {
        'type': 'xtls',
        'sni': sni,
        'flow': xtlsFlow
    }
    streamInfo['server']['security'] = 'xtls'
    streamInfo['server']['xtlsSettings'] = {
        'alpn': [
            'h2',
            'http/1.1'
        ],
        'certificates': [
            {
                'certificateFile': cert,
                'keyFile': key
            }
        ]
    }
    if xtlsFlow == 'xtls-origin':
        return 'xtls-rprx-origin', streamInfo
    elif xtlsFlow == 'xtls-direct':
        return 'xtls-rprx-direct', streamInfo
    elif xtlsFlow == 'xtls-splice':
        return 'xtls-rprx-direct', streamInfo
    else:
        raise Exception('Unknown XTLS flow')
