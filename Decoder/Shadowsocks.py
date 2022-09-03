#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SIP002: https://shadowsocks.org/guide/sip002.html
# Plain / Common: https://shadowsocks.org/guide/configs.html#uri-and-qr-code

from Basis.Logger import logging
from Basis.Functions import urlDecode
from Basis.Exception import decodeException


def ssBasicConfig() -> dict:  # load shadowsocks basic config
    return {
        'type': 'ss',
        'info': {}
    }


def ssPlain(url: str, spaceRemark: bool = True) -> dict:
    """
    FORMAT: ss://method:password@hostname:port#TAG
    """
    config = ssBasicConfig()
    logging.debug('Shadowsocks plain decode -> %s' % url)
    if not url.startswith('ss://'):
        logging.debug('Shadowsocks url should start with `ss://`')
        raise decodeException('Shadowsocks prefix error')
    url = url[5:]  # remove `ss://`
    if '#' in url:
        url, remark = url.rsplit('#', 1)  # split remark
        if spaceRemark:  # use `+` instead of space
            remark = remark.replace('+', ' ')
        config['name'] = urlDecode(remark)
        logging.debug('Shadowsocks url remark -> %s' % config['name'])
    userinfo, url = url.rsplit('@', 1)
    config['info']['server'], config['info']['port'] = url.rsplit(':', 1)
    config['info']['method'], config['info']['passwd'] = userinfo.split(':', 1)
    logging.debug('Shadowsocks plain release -> %s', config)
    return config

