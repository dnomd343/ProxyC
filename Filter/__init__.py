#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Filter.Brook import brookFilter
from Filter.VMess import vmessFilter
from Filter.VLESS import vlessFilter
from Filter.Trojan import trojanFilter
from Filter.Shadowsocks import ssFilter
from Filter.ShadowsocksR import ssrFilter
from Filter.TrojanGo import trojanGoFilter
from Filter.Hysteria import hysteriaFilter

filterEntry = {
    'ss': ssFilter,
    'ssr': ssrFilter,
    'vmess': vmessFilter,
    'vless': vlessFilter,
    'trojan': trojanFilter,
    'trojan-go': trojanGoFilter,
    'brook': brookFilter,
    'hysteria': hysteriaFilter,
}

def Filter(proxyType: str, proxyInfo: dict) -> dict:
    if proxyType not in filterEntry:
        raise RuntimeError('Unknown proxy type')
    return filterEntry[proxyType](proxyInfo)
