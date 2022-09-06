#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import urllib.parse

def urlEncode(content: str) -> str:  # url encode (RFC3986)
    return urllib.parse.quote(content, encoding = 'utf-8')


def urlDecode(content: str) -> str:  # url decode (RFC3986)
    return urllib.parse.unquote(content, encoding = 'utf-8')


def base64Encode(content: str, urlSafe: bool = True, padding: bool = False) -> str:  # base64 encode
    content = base64.b64encode(content.encode(encoding = 'utf-8')).decode(encoding = 'utf-8')
    if urlSafe:
        content = content.replace('+', '-')  # `+` => `-`
        content = content.replace('/', '_')  # `/` => `_`
    if padding:
        return content
    return content.replace('=', '')  # remove `=` padding


def base64Decode(content: str) -> str:  # base64 decode
    try:
        content = content.replace('-', '+').replace('_', '/')  # compatible urlSafe
        if len(content) % 4 in range(2, 4):  # remainder -> 2 or 3
            content = content.ljust((len(content) // 4 + 1) * 4, '=')  # increase to 4n
        return base64.b64decode(content).decode(encoding = 'utf-8')
    except:
        raise RuntimeError('Invalid base64 encode')
