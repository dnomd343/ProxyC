#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import Shadowsocks
from ProxyFilter import ShadowsocksR
from ProxyFilter import VMess
from ProxyFilter import VLESS
from ProxyFilter import Trojan
from ProxyFilter import TrojanGo
from ProxyFilter import Brook
from ProxyFilter import Hysteria

def filte(raw: dict, isExtra: bool = False) -> tuple[bool, str or dict]:
    """
    代理信息过滤并格式化

        参数无效:
            return False, {reason}

        参数有效:
            return True, {
                'type': '...',
                '...': '...',
                ...
            }
    """
    try:
        if 'type' not in raw:
            return False, 'Missing `type` option'
        if raw['type'] == 'ss':
            status, raw['info'] = Shadowsocks.ssFilter(raw['info'], isExtra)
        elif raw['type'] == 'ssr':
            status, raw['info'] = ShadowsocksR.ssrFilter(raw['info'], isExtra)
        elif raw['type'] == 'vmess':
            status, raw['info'] = VMess.vmessFilter(raw['info'], isExtra)
        elif raw['type'] == 'vless':
            status, raw['info'] = VLESS.vlessFilter(raw['info'], isExtra)
        elif raw['type'] == 'trojan':
            status, raw['info'] = Trojan.trojanFilter(raw['info'], isExtra)
        elif raw['type'] == 'trojan-go':
            status, raw['info'] = TrojanGo.trojanGoFilter(raw['info'], isExtra)
        elif raw['type'] == 'brook':
            status, raw['info'] = Brook.filte(raw['info'], isExtra)
        elif raw['type'] == 'hysteria':
            status, raw['info'] = Hysteria.filte(raw['info'], isExtra)
        else:
            return False, 'Unknown proxy type'
        return status, raw
    except:
        pass
    return False, 'Unknown error'
