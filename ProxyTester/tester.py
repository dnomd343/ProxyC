#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyTester import Shadowsocks

def test(key: str, config: dict) -> list:
    if key == 'ss':
        return Shadowsocks.ssTest(config)
    elif key == 'ssr':
        pass
    elif key == 'vmess':
        pass
    else:
        return []
