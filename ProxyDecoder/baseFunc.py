#!/usr/bin/python
# -*- coding:utf-8 -*-

import base64
import urllib.parse

def urlEncode(content: str) -> str or None:
    try:
        return urllib.parse.urlencode(content)
    except:
        return None

def urlDecode(content: str) -> str or None:
    try:
        return urllib.parse.unquote(content)
    except:
        return None

def base64Encode(content: str, urlSafe: bool = False, isPadding: bool = True) -> str or None:
    try:
        content = base64.b64encode(content.encode()).decode()
        if urlSafe:
            content = content.replace('+', '-')
            content = content.replace('/', '_')
        if not isPadding:
            content = content.replace('=', '')
        return content
    except:
        return None

def base64Decode(content: str) -> str or None:
    try:
        content = content.replace('-', '+').replace('_', '/')
        if len(content) % 4 in range(2, 4):  # remainder -> 2 or 3
            content = content.ljust((len(content) // 4 + 1) * 4, '=')  # increase to 4n
        return base64.b64decode(content).decode()
    except:
        return None
