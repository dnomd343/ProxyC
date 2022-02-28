#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import json
from ProxyDecoder import baseFunc

def __vmessV2raynDecode(url: str) -> dict:
    """
    v2rayN / v2rayNG分享链接解码

    FORMAT: vmess://BASE64-ENCODED-JSON-STRING

        {
          "v": "2",
          "ps": "...",
          "add": "...",
          "port": "...",
          "id": "...",
          "aid": "...",
          "scy": "...",
          "net": "...",
          "type": "...",
          "host": "...",
          "path": "...",
          "tls": "...",
          "sni": "...",
          "alpn": "..."
        }
    """
    content = json.loads(
        baseFunc.base64Decode(
            re.search(r'^vmess://([\S]+)$', url).group(1) # vmess://{base64}
        )
    )
    if int(content['v']) != 2: # version => 2
        raise Exception('Unknown version field')
    info = {
        'server': content['add'],
        'port': int(content['port']),
        'id': content['id'],
        'aid': int(content['aid']),
    }
    if 'ps' in content: # ps -> remark
        info['remark'] = content['ps']
    if 'scy' in content: # scy -> method
        info['method'] = content['scy']
    stream = {
        'type': content['net'] # net -> stream.type
    }
    if content['net'] == 'tcp':
        if 'http' in content and content['type'] == 'http': # type -> none / http
            stream['obfs'] = {
                'host': content['host'],
                'path': content['path']
            }
    elif content['net'] == 'kcp':
        if 'type' in content:
            stream['obfs'] = content['type']
        if 'path' in content:
            stream['seed'] = content['path'] # path -> seed
    elif content['net'] == 'ws':
        if 'host' in content:
            stream['host'] = content['host']
        if 'path' in content:
            try:
                stream['ed'], stream['path'] = baseFunc.splitEdParam(content['path'])
            except:
                stream['path'] = content['path']
    elif content['net'] == 'h2':
        if 'host' in content:
            stream['host'] = content['host']
        if 'path' in content:
            stream['path'] = content['path']
    elif content['net'] == 'quic':
        if 'type' in content:
            stream['obfs'] = content['type']
        if 'host' in content:
            stream['method'] = content['host']
        if 'path' in content:
            stream['passwd'] = content['path']
    elif content['net'] == 'grpc':
        if 'type' in content and content['type'] == 'multi':
            stream['mode'] = 'multi'
        if 'path' in content:
            stream['service'] = content['path']
    else:
        raise Exception('Unknown network type')

    secure = None
    if 'tls' in content and content['tls'] == 'tls': # enable TLS
        secure = {}
        if 'sni' in content:
            secure['sni'] = content['sni'] # sni option
        if 'alpn' in content:
            if content['alpn'] == '':
                secure['alpn'] = None # ignore alpn option
            else:
                secure['alpn'] = content['alpn'] # h2 | http/1.1 | h2,http/1.1

    stream['secure'] = secure
    info['stream'] = stream
    return info

def __vmessCommonDecode(url: str) -> dict:
    """
    VMess标准分享链接解码 (only VMessAEAD)

    FORMAT: vmess://$(UUID)@server:port?{fields}#$(remark)

        type -> tcp / kcp / ws / http / quic / grpc

        encryption -> auto / aes-128-gcm / chacha20-poly1305

        security -> none / tls

        path -> WebSocket / HTTP/2 / http obfs

        host -> WebSocket / HTTP/2 / http obfs

        headerType -> mKCP / QUIC UDP obfs -> none / srtp / utp / wechat-video / dtls / wireguard
                   -> TCP (http obfs) -> http

        seed -> mKCP seed

        quicSecurity -> QUIC method

        key -> QUIC key

        serviceName -> gRPC Service Name

        mode -> gRPC transport mode -> gun / multi / guna

        sni -> TLS SNI

        alpn -> TLS ALPN

    """
    match = re.search(r'^vmess://([\S]+?)(#[\S]*)?$', url) # vmess://...#REMARK
    remark = baseFunc.urlDecode(
        match[2][1:] if match[2] is not None else ''
    )
    match = re.search(
        r'^([\S]+)@([a-zA-Z0-9.:\-_\[\]]+):([0-9]+)/?([\S]*)$', match[1]
    )
    info = {
        'server': baseFunc.formatHost(match[2]),
        'port': int(match[3]),
        'id': baseFunc.urlDecode(match[1]),
        'remark': remark
    }
    params = baseFunc.paramSplit(match[4])
    if 'encryption' in params:
        info['method'] = params['encryption']
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

    secure = None
    if 'security' in params and params['security'] == 'tls':
        secure = {}
        if 'sni' in params:
            secure['sni'] = params['sni']
        if 'alpn' in params:
            secure['alpn'] = params['alpn']

    stream['secure'] = secure
    info['stream'] = stream
    return info

def vmessDecode(url: str) -> dict or None:
    """
    VMess分享链接解码

        链接合法:
            return {
                'type': 'vmess',
                ...
            }

        链接不合法:
            return None
    """
    if url[0:8] != 'vmess://':
        return None
    try:
        result = __vmessV2raynDecode(url) # try v2rayN decode
    except:
        try:
            result = __vmessCommonDecode(url)  # try VMess common decode
        except:
            return None
    result['type'] = 'vmess'
    return result
