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
    match = re.search(r'^ssr://([\S]+)$', url) # ssr://{BASE64}
    match = re.search(
        r'^([a-zA-Z0-9.:\-_\[\]]*):([0-9]*):' # server:port:
        r'([0-9a-zA-Z_.\-]*):([0-9a-zA-Z_.\-]*):([0-9a-zA-Z_.\-]*):' # protocol:method:obfs:
        r'([a-zA-Z0-9\-_+\\=]*)(/\?)?([\S]*)?$', # BASE64(passwd)/?...
        baseFunc.base64Decode(match[1])
    )
    info = {
        'server': baseFunc.formatHost(match[1]),
        'port': int(match[2]),
        'passwd': baseFunc.base64Decode(match[6]),
        'method': match[4],
        'protocol': match[3],
        'obfs': match[5],
    }
    params = baseFunc.paramSplit(match[8]) # /?obfsparam=...&protoparam=...&remarks=...&group=...
    if 'protoparam' in params:
        info['protocolParam'] = baseFunc.base64Decode(params['protoparam'])
    if 'obfsparam' in params:
        info['obfsParam'] = baseFunc.base64Decode(params['obfsparam'])
    if 'remarks' in params:
        info['remark'] = baseFunc.base64Decode(params['remarks'])
    if 'group' in params:
        info['group'] = baseFunc.base64Decode(params['group'])
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
