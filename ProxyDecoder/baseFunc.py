#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
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

def formatHost(content: str) -> str:
    try:
        content = content.lower().strip()
        if content[:1] == '[' and content[-1:] == ']':
            return content[1:-1]
    except:
        pass
    return content

def paramSplit(content: str) -> dict:
    if content.startswith('?'):
        content = content[1:]
    result = {}
    for field in content.split('&'):
        match = re.search(r'^([\S]*?)=([\S]*)$', field)  # xxx=...
        try:
            result[urlDecode(match[1])] = urlDecode(match[2])
        except:
            pass
    return result

def splitEdParam(path: str) -> tuple[int or None, str]: # 分离early-data参数
    if path.find('?') == -1:
        return None, path
    content = re.search(r'^([\s\S]*?)\?([\s\S]*)$', path)
    ed = None
    params = []
    for field in content[2].split('&'): # ?param_a=...&param_b=...
        if not field.startswith('ed='):
            params.append(field)
            continue
        ed = int(field[3:]) # ed=...
    if ed is None: # ed param not found
        return None, path
    if not params: # param -> []
        return ed, content[1]
    return ed, content[1] + '?' + '&'.join(params)
