#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import Shadowsocks
from ProxyFilter import ShadowsocksR

def filte(raw: dict, isExtra: bool = False) -> tuple[bool, str]:
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
            return Shadowsocks.ssFilter(raw, isExtra)
        elif raw['type'] == 'ssr':
            return ShadowsocksR.ssrFilter(raw, isExtra)
        else:
            return False, 'Unknown proxy type'
    except:
        pass
    return False, 'Unknown error'
