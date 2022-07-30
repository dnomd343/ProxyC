#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Builder import V2ray
from Basis.Methods import xtlsFlows

loadConfig = V2ray.loadConfig


def loadSecure(secureInfo: dict or None) -> dict:  # TLS / XTLS encrypt config
    if secureInfo is None:
        return {'security': 'none'}  # without TLS / XTLS options
    if secureInfo['type'] not in ['tls', 'xtls']:
        raise RuntimeError('Unknown secure type')
    secureObject = {
        'allowInsecure': not secureInfo['verify']  # whether verify server's certificate
    }
    if secureInfo['alpn'] is not None:
        secureObject['alpn'] = secureInfo['alpn'].split(',')  # multi-alpn like `h2,http/1.1`
    if secureInfo['sni'] != '':
        secureObject['serverName'] = secureInfo['sni']  # SNI field in TLS / XTLS protocol
    return {
        'security': secureInfo['type'],
        '%sSettings' % secureInfo['type']: secureObject
    }


def wsStream(streamInfo: dict) -> dict:  # WebSocket stream config (different ed config with v2fly-core)
    wsObject = {
        'path': streamInfo['path']  # websocket connection path
    }
    if streamInfo['host'] != '':  # empty host should not be set
        wsObject['headers'] = {}
        wsObject['headers']['Host'] = streamInfo['host']
    if streamInfo['ed'] is not None:  # ed value into uri path -> /...?ed=xxx
        if wsObject['path'].find('?') == -1:  # no params in raw path
            wsObject['path'] += '?ed=' + str(streamInfo['ed'])
        else:
            wsObject['path'] += '&ed=' + str(streamInfo['ed'])
    return {
        'network': 'ws',
        'wsSettings': wsObject
    }


def loadStream(streamInfo: dict) -> dict:
    streamEntry = {
        'tcp': V2ray.tcpStream,
        'kcp': V2ray.kcpStream,
        'ws': wsStream,  # different with v2fly-core
        'h2': V2ray.h2Stream,
        'quic': V2ray.quicStream,
        'grpc': V2ray.grpcStream,
    }
    if streamInfo['type'] not in streamEntry:
        raise RuntimeError('Unknown stream type')
    streamObject = streamEntry[streamInfo['type']](streamInfo)
    return {
        **streamObject,
        **loadSecure(streamInfo['secure'])
    }


def xtlsFlow(streamInfo: dict or None) -> dict:
    if streamInfo['secure'] is None:  # without TLS / XTLS options
        return {}
    if streamInfo['secure']['type'] != 'xtls':  # not XTLS secure type
        return {}
    if streamInfo['secure']['flow'] not in xtlsFlows:
        raise RuntimeError('Unknown xtls flow')
    return {
        'flow': xtlsFlows[streamInfo['secure']['flow']] + (  # xtls-rprx-xxx
            '-udp443' if streamInfo['secure']['udp443'] else ''  # whether block udp/443 (disable http/3)
        )
    }
