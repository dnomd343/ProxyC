#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
from ProxyDecoder import Shadowsocks
from ProxyDecoder import ShadowsocksR
from ProxyDecoder import VMess
from ProxyDecoder import VLESS
from ProxyDecoder import Trojan
from ProxyDecoder import TrojanGo
from ProxyDecoder import Brook

def decode(url: str) -> dict or None:
    """
    代理分享链接解码

        链接无效:
            return None

        链接有效:
            return {
                'type': ...,
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
        elif scheme == 'vless':
            return VLESS.vlessDecode(url)
        elif scheme == 'trojan':
            return Trojan.trojanDecode(url)
        elif scheme == 'trojan-go':
            return TrojanGo.trojanGoDecode(url)
        elif scheme == 'brook':
            return Brook.decode(url)
    except:
        pass
    return None
