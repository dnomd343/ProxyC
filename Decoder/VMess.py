#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from Utils.Logger import logger
from Utils.Exception import decodeException
from Utils.Common import base64Decode, checkScheme, hostFormat

def v2rayN(url: str) -> dict:
    """
    FORMAT: vmess://BASE64-ENCODED-JSON-STRING
            fields => v(=2) / ps / add / port / id / aid / scy / net / type / host / path / tls / sni / alpn
    """
    config = {
        'type': 'vmess',
        'info': {}
    }
    info = config['info']
    logger.debug('V2rayN url decode -> %s' % url)
    url = json.loads(base64Decode(checkScheme(url, 'vmess', 'V2rayN')))
    logger.debug('V2rayN json format -> %s' % url)
    if int(url['v']) != 2:
        logger.warning('V2rayN url with unknown version')

    config['name'] = url['ps'] if 'ps' in url else ''  # ps -> remark
    info = {
        'server': hostFormat(url['add']),
        'port': url['port'],
        'id': url['id'],
        'aid': url['aid'] if 'aid' in url else 0,  # default alter id -> 0
        'method': url['scy'] if 'scy' in url else 'auto',  # scy -> method (default = auto)
    }

    stream = {
        'type': url['net'] if 'net' in url else 'tcp' # net -> stream.type (default = tcp)
    }
    if stream['type'] == 'tcp':
        if 'http' in url and url['type'] == 'http': # type -> none / http
            stream['obfs'] = {
                'host': url['host'] if 'host' in url else '',
                'path': url['path'] if 'path' in url else '',
            }
    elif stream['type'] == 'kcp':
        stream['obfs'] = url['type'] if 'type' in url else 'none'  # type -> obfs
        stream['seed'] = url['path'] if 'path' in url else None  # path -> seed
    elif stream['type'] == 'ws':
        if 'host' in url:
            stream['host'] = url['host']
        if 'path' in url:
            try:
                stream['ed'], stream['path'] = baseFunc.splitEdParam(url['path'])
            except:
                stream['path'] = url['path']
    elif stream['type'] == 'h2':
        if 'host' in url:
            stream['host'] = url['host']
        if 'path' in url:
            stream['path'] = url['path']
    elif stream['type'] == 'quic':
        if 'type' in url:
            stream['obfs'] = url['type']
        if 'host' in url:
            stream['method'] = url['host']
        if 'path' in url:
            stream['passwd'] = url['path']
    elif stream['type'] == 'grpc':
        if 'type' in url and url['type'] == 'multi':
            stream['mode'] = 'multi'
        if 'path' in url:
            stream['service'] = url['path']
    else:
        logger.error('V2rayN url with unknown network type -> %s' % stream['type'])
        raise decodeException('Unknown v2rayN network type')

    info['stream'] = info
    logger.debug('V2rayN url release -> %s', config)
    logger.critical(stream)
    logger.critical(info)
