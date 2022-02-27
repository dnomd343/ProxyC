#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
from ProxyDecoder import Shadowsocks
from ProxyDecoder import ShadowsocksR
from ProxyDecoder import VMess

def decode(url: str) -> dict or None:
    """
    代理分享链接解码

        链接无效:
            return None

        链接有效:
            return {
                '...': '...',
                '...': '...',
                ...
            }
    """
    try:
        scheme = re.search(r'^([\S]+?)://([\s\S]+)$', url).group(1)
        if scheme == 'ss':
            return Shadowsocks.ssDecode(url, compatible = True)
        elif scheme == 'ssr':
            return ShadowsocksR.ssrDecode(url)
        elif scheme == 'vmess':
            return VMess.vmessDecode(url)
    except:
        pass
    return None
