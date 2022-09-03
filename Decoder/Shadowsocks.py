#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SIP002: https://shadowsocks.org/guide/sip002.html
# Plain / Common: https://shadowsocks.org/guide/configs.html#uri-and-qr-code

import copy
from Basis.Logger import logging
from Basis.Exception import decodeException
from Basis.Functions import base64Decode, urlDecode

ssBasicConfig = {
    'type': 'ss',
    'info': {}
}


def checkPrefix(url: str) -> str:  # check url prefix and remove it
    if not url.startswith('ss://'):
        logging.debug('Shadowsocks url should start with `ss://`')
        raise decodeException('Shadowsocks prefix error')
    return url[5:]


def splitTag(url: str, fromLeft: bool = True, spaceRemark: bool = True) -> tuple[str, str]:  # split tag after `#`
    if '#' not in url:  # without tag
        return url, ''
    if fromLeft:
        url, remark = url.split('#', 1)  # from left search
    else:
        url, remark = url.rsplit('#', 1)  # from right search
    if spaceRemark:  # deal with space remark for space
        remark = remark.replace('+', ' ')
    return url, urlDecode(remark)


def ssPlain(url: str) -> dict:
    """
    FORMAT: ss://method:password@hostname:port[#TAG]
    """
    config = copy.deepcopy(ssBasicConfig)
    logging.debug('Shadowsocks plain decode -> %s' % url)
    url, config['name'] = splitTag(checkPrefix(url), False)
    userinfo, url = url.rsplit('@', 1)
    config['info']['server'], config['info']['port'] = url.rsplit(':', 1)
    config['info']['method'], config['info']['passwd'] = userinfo.split(':', 1)
    logging.debug('Shadowsocks plain decode release -> %s', config)
    return config


def ssCommon(url: str) -> dict:
    """
    FORMAT: ss://BASE64-ENCODED-STRING-WITHOUT-PADDING[#TAG]
            base64('method:password@hostname:port')
    """
    config = copy.deepcopy(ssBasicConfig)
    logging.debug('Shadowsocks common decode -> %s' % url)
    url, config['name'] = splitTag(checkPrefix(url))
    userinfo, url = base64Decode(url).rsplit('@', 1)
    config['info']['server'], config['info']['port'] = url.rsplit(':', 1)
    config['info']['method'], config['info']['passwd'] = userinfo.split(':', 1)
    logging.debug('Shadowsocks common decode release -> %s', config)
    return config


def sip002(url: str) -> dict:
    """
    FORMAT: ss://userinfo@hostname:port [ "/" ] [ "?" plugin ] [ #tag ]
            userinfo => method:password or websafe-base64-encode-utf8(method:password)
    """
    config = copy.deepcopy(ssBasicConfig)
    logging.debug('Shadowsocks sip002 decode -> %s' % url)
    url, config['name'] = splitTag(checkPrefix(url))
    userinfo, url = url.rsplit('@', 1)
    try:
        userinfo = base64Decode(userinfo)  # userinfo encode base64 is optional
    except:
        userinfo = urlDecode(userinfo)  # not base64 decode -> url encode format
    config['info']['method'], config['info']['passwd'] = userinfo.split(':', 1)
    url = url.replace('/?plugin=', '?plugin=')  # remove `/` character
    if '?plugin=' in url:
        url, plugin = url.split('?plugin=', 1)
        plugin = urlDecode(plugin).split(';', 1)
        config['info']['plugin'] = {
            'type': plugin[0],
            'param': '' if len(plugin) == 1 else plugin[1]  # default as empty string
        }
    config['info']['server'], config['info']['port'] = url.rsplit(':', 1)
    logging.debug('Shadowsocks sip002 decode release -> %s', config)
    return config
