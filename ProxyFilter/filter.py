#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyFilter import Shadowsocks

def filter(raw):
    '''
    代理信息过滤并格式化

        参数无效:
            return False, {reason}

        参数有效:
            return True, {
                '...': '...',
                '...': '...',
                ...
            }

    '''
    try:
        if not 'type' in raw:
            return False, 'Missing `type` option'
        if raw['type'] == 'ss':
            return Shadowsocks.ssFilter(raw)
        else:
            return False, 'Unknown proxy type'
    except:
        pass
    return False, 'Unknown error'
