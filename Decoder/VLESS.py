#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Utils.Logger import logger
from Decoder.V2ray import v2ray
from Utils.Common import checkScheme, splitTag

def vless(url: str) -> dict:
    """
    https://github.com/XTLS/Xray-core/discussions/716

    FORMAT: aka Decoder.V2ray
    """
    config = {
        'type': 'vless'
    }
    logger.debug('VLESS url decode -> %s' % url)
    url, config['name'] = splitTag(checkScheme(url, 'vless', 'VLESS'))
    config['info'] = v2ray(url, isXtls = True)
    logger.debug('VLESS url release -> %s' % config)
    return config
