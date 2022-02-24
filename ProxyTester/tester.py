#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyTester import Shadowsocks

testInfo = {
    'type': 'ss',
    'method': 'aes-256-ctr',
    'plugin': None
}

def test(key: str) -> list:
    if key == 'ss':
        return Shadowsocks.ssTest()
    elif key == 'ssr':
        pass
    elif key == 'vmess':
        pass
    else:
        return []
