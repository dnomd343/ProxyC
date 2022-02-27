#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyTester import Shadowsocks
from ProxyTester import ShadowsocksR
from ProxyTester import VMess
from ProxyTester import VLESS
from ProxyTester import Trojan

def test(key: str, config: dict) -> list:
    if key in ['ss', 'shadowsocks']:
        return Shadowsocks.ssTest(config)
    elif key in ['ssr', 'shadowsocksr']:
        return ShadowsocksR.ssrTest(config)
    elif key == 'vmess':
        return VMess.vmessTest(config)
    elif key == 'vless':
        return VLESS.vlessTest(config)
    elif key == 'trojan':
        return Trojan.trojanTest(config)
    else:
        return []
