#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyTester import Shadowsocks
from ProxyTester import ShadowsocksR
from ProxyTester import VMess
from ProxyTester import VLESS
from ProxyTester import Trojan
from ProxyTester import TrojanGo
from ProxyTester import Brook
from ProxyTester import Hysteria

def test(key: str, config: dict) -> list:
    if key in ['ss', 'shadowsocks']:
        testObj = Shadowsocks
    elif key in ['ssr', 'shadowsocksr']:
        testObj = ShadowsocksR
    elif key == 'vmess':
        testObj = VMess
    elif key == 'vless':
        testObj = VLESS
    elif key == 'trojan':
        testObj = Trojan
    elif key == 'trojan-go':
        testObj = TrojanGo
    elif key == 'brook':
        testObj = Brook
    elif key == 'hysteria':
        testObj = Hysteria
    else:
        return []
    return testObj.test(config)
