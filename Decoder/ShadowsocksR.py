#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# https://github.com/shadowsocksrr/shadowsocksr-csharp/blob/master/shadowsocks-csharp/Model/Server.cs#L357

from Utils.Logger import logger
from Utils.Common import b64Decode, checkScheme, splitParam

def ssr(url: str) -> dict:
    """
    FORMAT: ssr://base64(
                server:port:protocol:method:obfs:base64(passwd)/?
                obfsparam=base64(...)&protoparam=...(...)&remarks=base64(...)&group=base64(...)
            )
    """
    config = {
        'type': 'ssr',
        'info': {}
    }
    info = config['info']
    logger.debug('ShadowsocksR decode -> %s' % url)

    params = ''
    url = b64Decode(checkScheme(url, 'ssr', 'ShadowsocksR'))
    if '?' in url:
        url, params = url.replace('/?', '?').split('?')  # `.../?...` or `...?...`
    info['server'], info['port'], info['protocol'], info['method'], info['obfs'], info['passwd'] = url.rsplit(':', 5)
    info['passwd'] = b64Decode(info['passwd'])

    params = splitParam(params)
    logger.debug('ShadowsocksR decode params -> %s' % params)
    info['obfsParam'] = b64Decode(params['obfsparam']) if 'obfsparam' in params else ''
    info['protocolParam'] = b64Decode(params['protoparam']) if 'protoparam' in params else ''
    config['name'] = b64Decode(params['remarks']) if 'remarks' in params else ''
    config['group'] = b64Decode(params['group']) if 'group' in params else ''
    logger.debug('ShadowsocksR decode release -> %s', config)
    return config
