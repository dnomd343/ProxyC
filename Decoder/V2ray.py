#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Utils.Logger import logger
from Utils.Exception import decodeException
from Utils.Common import splitParam, splitEdParam


def tlsSecure(params: dict) -> dict or None:
    if params['security'] == 'tls':
        return {
            'sni': params['sni'] if 'sni' in params else '',  # sni option
            'alpn': params['alpn'] if 'alpn' in params and params['alpn'] != '' else None  # alpn option
        }
    elif params['security'] in ['', 'none']:
        return None
    logger.error('V2ray url with unknown secure type -> %s' % params['security'])
    raise decodeException('Unknown v2ray secure type')


def xtlsSecure(params: dict) -> dict or None:
    if params['security'] in ['tls', 'xtls']:
        secure = {
            'type': params['security'],
            'sni': params['sni'] if 'sni' in params else '',  # sni option
            'alpn': params['alpn'] if 'alpn' in params and params['alpn'] != '' else None  # alpn option
        }
        if params['security'] == 'xtls' and 'flow' in params:  # XTLS flow
            if 'origin' in params['flow']:
                secure['flow'] = 'xtls-origin'
            elif 'direct' in params['flow']:
                secure['flow'] = 'xtls-direct'
            elif 'splice' in params['flow']:
                secure['flow'] = 'xtls-splice'
            else:
                logger.error('XTLS with unknown flow type -> %s' % params['flow'])
                raise decodeException('Unknown xtls flow type')
        return secure
    elif params['security'] in ['', 'none']:
        return None
    logger.error('V2ray url with unknown secure type -> %s' % params['security'])
    raise decodeException('Unknown v2ray secure type')


def v2ray(url: str, isXtls: bool) -> dict:  # include VMess and VLESS
    """
    https://github.com/XTLS/Xray-core/discussions/716

    FORMAT: scheme://UUID@server:port?fields#remark
        scheme -> vmess / vless
        type -> tcp / kcp / ws / http / quic / grpc
        encryption -> auto / aes-128-gcm / chacha20-poly1305 (VMess)
                   -> none (VLESS)
        security -> none / tls / xtls (VMess without xtls)
        path -> WebSocket / HTTP/2 / http obfs
        host -> WebSocket / HTTP/2 / http obfs
        headerType -> mKCP / QUIC UDP obfs -> none / srtp / utp / wechat-video / dtls / wireguard
                   -> TCP (http obfs) -> http
        serviceName -> gRPC Service Name
        mode -> gRPC transport mode -> gun / multi / guna
        sni -> TLS / XTLS SNI (VMess without XTLS)
        alpn -> TLS / XTLS ALPN (VMess without XTLS)
        flow -> XTLS flow type -> xtls-rprx-origin / xtls-rprx-direct / xtls-rprx-splice (VMess without xtls)
    """
    params = ''
    if '?' in url:
        url, params = url.replace('/?', '?').split('?')  # `.../?...` or `...?...`
    params = splitParam(params)

    info = {}
    info['id'], url = url.rsplit('@', 1)
    info['server'], info['port'] = url.rsplit(':', 1)
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
        logger.error('V2ray url with unknown network type -> %s' % stream['type'])
        raise decodeException('Unknown v2ray network type')

    if 'security' in params:  # enable TLS / XTLS
        if not isXtls:
            stream['secure'] = tlsSecure(params)
        else:
            stream['secure'] = xtlsSecure(params)
    info['stream'] = stream
    return info
