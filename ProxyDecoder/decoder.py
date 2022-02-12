#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyDecoder import Shadowsocks

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
        return Shadowsocks.ssDecode(url)
    except:
        pass
    return None
