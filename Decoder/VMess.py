#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# VMess / VLESS: https://github.com/XTLS/Xray-core/discussions/716
# V2rayN: https://github.com/2dust/v2rayN/wiki/%E5%88%86%E4%BA%AB%E9%93%BE%E6%8E%A5%E6%A0%BC%E5%BC%8F%E8%AF%B4%E6%98%8E(ver-2)

import json
from Utils.Logger import logger
from Utils.Exception import decodeException
from Utils.Common import b64Decode, checkScheme
from Utils.Common import hostFormat, splitTag, splitEdParam, splitParam

def v2rayN(url: str) -> dict:
    """
    FORMAT: vmess://BASE64-ENCODED-JSON-STRING
            fields => v(=2) / ps / add / port / id / aid / scy / net / type / host / path / tls / sni / alpn
    """
    logger.debug('V2rayN url decode -> %s' % url)
    url = json.loads(b64Decode(checkScheme(url, 'vmess', 'V2rayN')))
    logger.debug('V2rayN json format -> %s' % url)
    if int(url['v']) != 2:
        logger.warning('V2rayN url with unknown version')

    config = {
        'type': 'vmess',
        'name': url['ps'] if 'ps' in url else '',  # ps -> remark
        'info': {
            'server': hostFormat(url['add']),
            'port': url['port'],
            'id': url['id'],
            'aid': url['aid'] if 'aid' in url else 0,  # default alter id -> 0
            'method': url['scy'] if 'scy' in url else 'auto',  # scy -> method (default = auto)
        }
    }
    stream = {
        'type': url['net'] if 'net' in url else 'tcp'  # net -> stream.type (default = tcp)
    }
    if stream['type'] == 'tcp':
        if 'http' in url and url['type'] == 'http': # type -> obfs
            stream['obfs'] = {
                'host': url['host'] if 'host' in url else '',
                'path': url['path'] if 'path' in url else '/',
            }
    elif stream['type'] == 'kcp':
        stream['obfs'] = url['type'] if 'type' in url else 'none'  # type -> obfs
        stream['seed'] = url['path'] if 'path' in url else None  # path -> seed
    elif stream['type'] == 'ws':
        stream['host'] = url['host'] if 'host' in url else ''  # host -> host
        if 'path' in url:
            try:
                stream['path'], stream['ed'] = splitEdParam(url['path'])
            except:
                stream['path'] = url['path']
    elif stream['type'] == 'h2':
        stream['host'] = url['host'] if 'host' in url else ''  # host -> host
        stream['path'] = url['path'] if 'path' in url else '/'  # path -> path
    elif stream['type'] == 'quic':
        stream['obfs'] = url['type'] if 'type' in url else 'none'  # type -> obfs
        stream['method'] = url['host'] if 'host' in url else 'none'  # host -> method
        stream['passwd'] = url['path'] if 'path' in url else ''  # path -> passwd
    elif stream['type'] == 'grpc':
        stream['mode'] = 'multi' if 'type' in url and url['type'] == 'multi' else 'gun'  # type -> mode
        stream['service'] = url['path']  # path -> service
    else:
        logger.error('V2rayN url with unknown network type -> %s' % stream['type'])
        raise decodeException('Unknown v2rayN network type')

    secure = None
    if 'tls' in url and url['tls'] == 'tls':  # enable TLS
        secure = {
            'sni': url['sni'] if 'sni' in url else '',  # sni option
            'alpn': url['alpn'] if 'alpn' in url and url['alpn'] != '' else None  # alpn option
        }
    stream['secure'] = secure
    config['info']['stream'] = stream
    logger.debug('V2rayN url release -> %s', config)
    return config


def vmess(url: str) -> dict:
    """
    FORMAT: vmess://UUID@server:port?fields#remark
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
    config = {
        'type': 'vmess',
        'info': {}
    }
    info = config['info']
    logger.debug('VMess url decode -> %s' % url)
    url, config['name'] = splitTag(checkScheme(url, 'vmess', 'VMess'))

    params = ''
    if '?' in url:
        url, params = url.replace('/?', '?').split('?')  # `.../?...` or `...?...`
    params = splitParam(params)

    config['info']['id'], url = url.rsplit('@', 1)
    config['info']['server'], config['info']['port'] = url.rsplit(':', 1)

    # split params
    if 'encryption' in params:
        info['method'] = params['encryption']
    stream = {
        'type': params['type'] if 'type' in params else 'tcp'  # stream type (default = tcp)
    }
    stream['type'] = 'h2' if stream['type'] == 'http' else stream['type']  # http -> h2

    if stream['type'] == 'tcp':
        if 'headerType' in params and params['headerType'] == 'http':
            stream['obfs'] = {
                'host': params['host'] if 'host' in params else '',
                'path': params['path'] if 'path' in params else '/',
            }
    elif stream['type'] == 'kcp':
        stream['obfs'] = params['headerType'] if 'headerType' in params else 'none'
        stream['seed'] = params['seed'] if 'seed' in params else None
    elif stream['type'] == 'ws':
        stream['host'] = params['host'] if 'host' in params else ''
        if 'path' in params:
            try:
                stream['path'], stream['ed'] = splitEdParam(params['path'])
            except:
                stream['path'] = params['path']
    elif stream['type'] == 'h2':
        stream['host'] = params['host'] if 'host' in params else ''
        stream['path'] = params['path'] if 'path' in params else '/'
    elif stream['type'] == 'quic':
        stream['obfs'] = params['headerType'] if 'headerType' in params else 'none'
        stream['method'] = params['quicSecurity'] if 'quicSecurity' in params else 'none'
        stream['passwd'] = params['key'] if 'key' in params else ''
    elif stream['type'] == 'grpc':
        stream['service'] = params['serviceName']
        stream['mode'] = 'multi' if 'mode' in params and params['mode'] == 'multi' else 'gun'
    else:
        logger.error('VMess url with unknown network type -> %s' % stream['type'])
        raise decodeException('Unknown vmess network type')

    if 'security' in params and params['security'] == 'tls':  # enable TLS
        stream['secure'] = {
            'sni': params['sni'] if 'sni' in params else '',  # sni option
            'alpn': params['alpn'] if 'alpn' in params and params['alpn'] != '' else None  # alpn option
        }
    config['info']['stream'] = stream
    return config
