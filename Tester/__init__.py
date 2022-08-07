#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Tester import Brook
from Tester import VMess
from Tester import VLESS
from Tester import Trojan
from Tester import TrojanGo
from Tester import Hysteria
from Tester import Shadowsocks
from Tester import ShadowsocksR

testEntry = {
    'ss': Shadowsocks.load(),
    'ss-all': Shadowsocks.load(isExtra = True),
    'ssr': ShadowsocksR.load(),
    'vmess': VMess.load(),
    'vless': VLESS.load(),
    'trojan': Trojan.load(),
    'trojan-go': TrojanGo.load(),
    'brook': Brook.load(),
    'hysteria': Hysteria.load(),
}
