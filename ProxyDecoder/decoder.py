#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
from ProxyDecoder import Shadowsocks
from ProxyDecoder import ShadowsocksR

def decode(url):
    '''
    代理分享链接解码

        链接无效:
            return None

        链接有效:
            return {
                '...': '...',
                '...': '...',
                ...
            }

    '''
    try:
        scheme = re.search(r'^([\S]+?)://([\s\S]+)$', url).group(1)
        if scheme == 'ss':
            return Shadowsocks.ssDecode(url)
        elif scheme == 'ssr':
            return ShadowsocksR.ssrDecode(url)
    except:
        pass
    return None