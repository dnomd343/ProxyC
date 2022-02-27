#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
from ProxyDecoder import baseFunc

def __ssrCommonDecode(url: str) -> dict:
    """
    ShadowsocksR经典分享链接解码

    FORMAT: ssr://BASE64-ENCODED-STRING-WITHOUT-PADDING

    EXAMPLE:
        ssr://{base64}
        -> server:port:protocol:method:obfs:base64(passwd)/?...
        -> obfsparam=...&protoparam=...&remarks=...&group=...
    """
    content = re.search(r'^ssr://([\S]+)$', url).group(1) # ssr://{base64}
    content = re.search(
        r'^([a-zA-Z0-9.:_-]*):([0-9]*):' # server:p/r
        r'([0-9a-zA-Z_.-]*):([0-9a-zA-Z_.-]*):([0-9a-zA-Z_.-]*):' # protocol:method:obfs:
        r'([0-9a-zA-Z_=+\\-]*)(/\?)?([\S]*)?$', # base(passwd)/?...
        baseFunc.base64Decode(content)
    )
    info = {
        'server': content.group(1),
        'port': int(content.group(2)),
        'passwd': baseFunc.base64Decode(content.group(6)),
        'method': content.group(4),
        'protocol': content.group(3),
        'obfs': content.group(5),
    }
    for field in content.group(8).split('&'): # /?obfsparam=...&protoparam=...&remarks=...&group=...
        if field.find('=') == -1: # 缺失xxx=...
            continue
        field = re.search(r'^([\S]*?)=([\S]*)$', field) # xxx=...
        if field.group(1) == 'protoparam':
            info['protocolParam'] = baseFunc.base64Decode(field.group(2))
        elif field.group(1) == 'obfsparam':
            info['obfsParam'] = baseFunc.base64Decode(field.group(2))
        elif field.group(1) == 'remarks':
            info['remark'] = baseFunc.base64Decode(field.group(2))
        elif field.group(1) == 'group':
            info['group'] = baseFunc.base64Decode(field.group(2))
    return info

def ssrDecode(url: str) -> dict or None:
    """
    ShadowsocksR分享链接解码

        链接合法:
            return {
                'type': 'ssr',
                ...
            }

        链接不合法:
            return None
    """
    if url[0:6] != 'ssr://':
        return None
    try:
        result = __ssrCommonDecode(url) # try common decode
    except:
        return None
    result['type'] = 'ssr'
    return result
