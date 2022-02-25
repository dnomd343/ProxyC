#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyTester import Shadowsocks
from ProxyTester import ShadowsocksR
from ProxyTester import VMess

def test(key: str, config: dict) -> list:
    if key == 'ss':
        return Shadowsocks.ssTest(config)
    elif key == 'ssr':
        return ShadowsocksR.ssrTest(config)
    elif key == 'vmess':
        return VMess.vmessTest(config)
    else:
        return []
