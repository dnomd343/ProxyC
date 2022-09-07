#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from Utils.Logger import logger
from Utils.Exception import decodeException
from Utils.Common import b64Decode, checkScheme
from Utils.Common import hostFormat, splitEdParam

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
