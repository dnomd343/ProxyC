#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
from ProxyDecoder import baseFunc

def __trojanCommonDecode(url: str) -> dict:
    """
    Trojan标准分享链接解码

    FORMAT: trojan://$(UUID)@server:port?{fields}#$(remark)

        type -> tcp / kcp / ws / http / quic / grpc

        encryption -> none

        security -> none / tls / xtls

        path -> WebSocket / HTTP/2 / http obfs

        host -> WebSocket / HTTP/2 / http obfs

        headerType -> mKCP / QUIC UDP obfs -> none / srtp / utp / wechat-video / dtls / wireguard
                   -> TCP (http obfs) -> http

        seed -> mKCP seed

        quicSecurity -> QUIC method

        key -> QUIC key

        serviceName -> gRPC Service Name

        mode -> gRPC transport mode -> gun / multi / guna

        sni -> TLS / XTLS SNI

        alpn -> TLS / XTLS ALPN

        flow -> XTLS flow type -> xtls-rprx-origin / xtls-rprx-direct / xtls-rprx-splice

    """
    match = re.search(r'^trojan://([\S]+?)(#[\S]*)?$', url) # trojan://...#REMARK
    remark = baseFunc.urlDecode(
        match[2][1:] if match[2] is not None else ''
    )
    match = re.search(
        r'^([\S]+)@([a-zA-Z0-9.:\-_\[\]]+):([0-9]+)/?([\S]*)$', match[1]
    )
    info = {
        'server': baseFunc.formatHost(match[2]),
        'port': int(match[3]),
        'passwd': baseFunc.urlDecode(match[1]),
        'remark': remark
    }
    params = baseFunc.paramSplit(match[4])
    if 'type' not in params:
        params['type'] = 'tcp' # default -> tcp
    stream = {
        'type': params['type']
    }
    if params['type'] == 'tcp':
        if 'headerType' in params and params['headerType'] == 'http':
            stream['obfs'] = {}
            if 'host' in params:
                stream['obfs']['host'] = params['host']
            if 'path' in params:
                stream['obfs']['path'] = params['path']
    elif params['type'] == 'kcp':
        if 'headerType' in params:
            stream['obfs'] = params['headerType']
        if 'seed' in params:
            stream['seed'] = params['seed']
    elif params['type'] == 'ws':
        if 'host' in params:
            stream['host'] = params['host']
        if 'path' in params:
            try:
                stream['ed'], stream['path'] = baseFunc.splitEdParam(params['path'])
            except:
                stream['path'] = params['path']
    elif params['type'] == 'http':
        if 'host' in params:
            stream['host'] = params['host']
        if 'path' in params:
            stream['path'] = params['path']
    elif params['type'] == 'quic':
        if 'headerType' in params:
            stream['obfs'] = params['headerType']
        if 'quicSecurity' in params:
            stream['method'] = params['quicSecurity']
        if 'key' in params:
            stream['passwd'] = params['key']
    elif params['type'] == 'grpc':
        if 'serviceName' in params:
            stream['service'] = params['serviceName']
        if 'mode' in params and params['mode'] == 'multi':
            stream['mode'] = 'multi'
    else:
        raise Exception('Unknown network type')

    if 'security' in params:
        if params['security'] not in ['tls', 'xtls']:
            raise Exception('Unknown security type')
        secure = {
            'type': params['security']
        }
        if 'sni' in params:
            secure['sni'] = params['sni']
        if 'alpn' in params:
            secure['alpn'] = params['alpn']
        if params['security'] == 'xtls' and 'flow' in params: # XTLS flow
            if params['flow'] in ['xtls-rprx-origin', 'xtls-rprx-origin-udp443']:
                secure['flow'] = 'xtls-origin'
            elif params['flow'] in ['xtls-rprx-direct', 'xtls-rprx-direct-udp443']:
                secure['flow'] = 'xtls-direct'
            elif params['flow'] in ['xtls-rprx-splice', 'xtls-rprx-splice-udp443']:
                secure['flow'] = 'xtls-splice'
        stream['secure'] = secure
    info['stream'] = stream
    return info

def trojanDecode(url: str) -> dict or None:
    """
    Trojan分享链接解码

        链接合法:
            return {
                'type': 'trojan',
                ...
            }

        链接不合法:
            return None
    """
    if url[0:9] != 'trojan://':
        return None
    try:
        result = __trojanCommonDecode(url)  # try Trojan common decode
    except:
        return None
    result['type'] = 'trojan'
    return result
