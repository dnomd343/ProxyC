#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import base64
import urllib.parse


def urlEncode(content: str) -> str or None: # url-encode
    try:
        return urllib.parse.urlencode(content)
    except:
        return None


def urlDecode(content: str) -> str or None: # url-decode
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


def formatHost(host: str) -> str: # host -> IP / Domain
    try:
        host = host.lower().strip()
        if host[:1] == '[' and host[-1:] == ']': # [IPv6]
            return host[1:-1]
    except:
        pass
    return host


def paramSplit(paramStr: str) -> dict: # ?param_1=xxx&param_2=xxx&param_3=xxx
    if paramStr.startswith('?'):
        paramStr = paramStr[1:] # remove `?` char
    params = {}
    for field in paramStr.split('&'):
        if field.find('=') < 0: # without `=` char
            continue
        key, value = field.split('=', maxsplit = 1)
        params[key] = urlDecode(value)
    return params


def splitEdParam(path: str) -> tuple[int or None, str]: # split early-data option
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


def urlSplit(url: str) -> dict: # scheme://[auth@]server[:port]/.../...?param_1=...&param_2=...#remark
    url = urllib.parse.urlparse(url)
    auth = port = None
    netloc = url[1]
    if not netloc.find(':') < 0: # server[:port]
        netloc, port = netloc.rsplit(':', maxsplit = 1)
        port = int(port)
    if not netloc.find('@') < 0: # [auth@]server
        auth, netloc = netloc.rsplit('@', maxsplit = 1)
    return {
        'scheme': url[0],
        'auth': auth,
        'server': formatHost(netloc),
        'port': port,
        'path': url[2],
        'params': paramSplit(url[4]),
        'remark': urlDecode(url[5])
    }
