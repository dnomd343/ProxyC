#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SIP002: https://shadowsocks.org/guide/sip002.html
# Plain / Common: https://shadowsocks.org/guide/configs.html#uri-and-qr-code

import copy
from Utils.Logger import logger
from Utils.Common import checkScheme, splitTag
from Utils.Common import urlDecode, base64Decode


ssBasicConfig = {
    'type': 'ss',
    'info': {}
}


def ssPlain(url: str) -> dict:
    """
    FORMAT: ss://method:password@hostname:port[#TAG]
    """
    config = copy.deepcopy(ssBasicConfig)
    logger.debug('Shadowsocks plain decode -> %s' % url)
    url, config['name'] = splitTag(checkScheme(url, 'ss', 'Shadowsocks plain'), fromRight = True)
    userinfo, url = url.rsplit('@', 1)
    config['info']['server'], config['info']['port'] = url.rsplit(':', 1)
    config['info']['method'], config['info']['passwd'] = userinfo.split(':', 1)
    logger.debug('Shadowsocks plain decode release -> %s', config)
    return config


def ssCommon(url: str) -> dict:
    """
    FORMAT: ss://BASE64-ENCODED-STRING-WITHOUT-PADDING[#TAG]
            base64('method:password@hostname:port')
    """
    config = copy.deepcopy(ssBasicConfig)
    logger.debug('Shadowsocks common decode -> %s' % url)
    url, config['name'] = splitTag(checkScheme(url, 'ss', 'Shadowsocks common'))
    userinfo, url = base64Decode(url).rsplit('@', 1)
    config['info']['server'], config['info']['port'] = url.rsplit(':', 1)
    config['info']['method'], config['info']['passwd'] = userinfo.split(':', 1)
    logger.debug('Shadowsocks common decode release -> %s', config)
    return config


def sip002(url: str) -> dict:
    """
    FORMAT: ss://userinfo@hostname:port [ "/" ] [ "?" plugin ] [ #tag ]
            userinfo => method:password or websafe-base64-encode-utf8(method:password)
    """
    config = copy.deepcopy(ssBasicConfig)
    logger.debug('SIP002 decode -> %s' % url)
    url, config['name'] = splitTag(checkScheme(url, 'ss', 'SIP002'))
    userinfo, url = url.rsplit('@', 1)
    try:
        userinfo = base64Decode(userinfo)  # userinfo encode base64 is optional
    except:
        userinfo = urlDecode(userinfo)  # not base64 decode -> url encode format
    config['info']['method'], config['info']['passwd'] = userinfo.split(':', 1)
    url = url.replace('/?plugin=', '?plugin=')  # remove `/` character
    if '?plugin=' in url:  # with sip003 plugin
        url, plugin = url.split('?plugin=', 1)
        plugin = urlDecode(plugin).split(';', 1)
        config['info']['plugin'] = {
            'type': plugin[0],
            'param': '' if len(plugin) == 1 else plugin[1]  # default as empty string
        }
    config['info']['server'], config['info']['port'] = url.rsplit(':', 1)
    logger.debug('SIP002 decode release -> %s', config)
    return config
