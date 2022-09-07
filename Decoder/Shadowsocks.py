#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SIP002: https://shadowsocks.org/guide/sip002.html
# SS Plain: https://shadowsocks.org/guide/configs.html#uri-and-qr-code

from Utils.Logger import logger
from Utils.Common import urlDecode, b64Decode
from Utils.Common import checkScheme, splitTag


def ss(url: str) -> dict:
    """
    FORMAT: ss://method:password@hostname:port[#TAG]
            ss://BASE64-ENCODED-STRING-WITHOUT-PADDING[#TAG]
                base64('method:password@hostname:port')
    """
    config = {
        'type': 'ss',
        'info': {}
    }
    info = config['info']
    logger.debug('Shadowsocks url decode -> %s' % url)
    url, config['name'] = splitTag(checkScheme(url, 'ss', 'Shadowsocks'), fromRight = True)
    try:
        userinfo, url = b64Decode(url).rsplit('@', 1)
    except:
        userinfo, url = url.rsplit('@', 1)
    info['server'], info['port'] = url.rsplit(':', 1)
    info['method'], info['passwd'] = userinfo.split(':', 1)
    logger.debug('Shadowsocks url release -> %s' % config)
    return config


def sip002(url: str) -> dict:
    """
    FORMAT: ss://userinfo@hostname:port [ "/" ] [ "?" plugin ] [ #tag ]
            userinfo => method:password or websafe-base64-encode-utf8(method:password)
    """
    config = {
        'type': 'ss',
        'info': {}
    }
    info = config['info']
    logger.debug('SIP002 url decode -> %s' % url)
    url, config['name'] = splitTag(checkScheme(url, 'ss', 'SIP002'))
    userinfo, url = url.rsplit('@', 1)
    try:
        userinfo = b64Decode(userinfo)  # userinfo encode base64 is optional
    except:
        userinfo = urlDecode(userinfo)  # not base64 decode -> url encode format
    info['method'], info['passwd'] = userinfo.split(':', 1)
    url = url.replace('/?plugin=', '?plugin=')  # remove `/` character
    if '?plugin=' in url:  # with sip003 plugin
        url, plugin = url.split('?plugin=', 1)
        plugin = urlDecode(plugin).split(';', 1)
        info['plugin'] = {
            'type': plugin[0],
            'param': '' if len(plugin) == 1 else plugin[1]  # default as empty string
        }
    info['server'], info['port'] = url.rsplit(':', 1)
    logger.debug('SIP002 url release -> %s' % config)
    return config
