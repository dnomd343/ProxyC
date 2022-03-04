#!/usr/bin/python
# -*- coding:utf-8 -*-

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
        scheme = url.split('://', maxsplit = 1)[0]
        if scheme == 'ss':
            return Shadowsocks.decode(url, compatible = True)
        elif scheme == 'ssr':
            return ShadowsocksR.decode(url)
        elif scheme == 'vmess':
            return VMess.decode(url)
        elif scheme == 'vless':
            return VLESS.decode(url)
        elif scheme == 'trojan':
            return Trojan.decode(url)
        elif scheme == 'trojan-go':
            return TrojanGo.decode(url)
        elif scheme == 'brook':
            return Brook.decode(url)
    except:
        pass
    return None
