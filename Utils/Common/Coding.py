#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import urllib.parse
from Utils.Logger import logger

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


def checkScheme(url: str, scheme: str, name: str) -> str:  # check url scheme and remove it
    if not url.startswith('%s://' % scheme):
        logger.debug('%s url should start with `%s://`', name, scheme)
        raise RuntimeError('%s scheme error', name)
    return url[len(scheme) + 3:]


def splitTag(url: str, fromRight: bool = True, spaceRemark: bool = True) -> tuple[str, str]:  # split tag after `#`
    if '#' not in url:  # without tag
        return url, ''
    if not fromRight:
        url, remark = url.split('#', 1)  # from left search
    else:
        url, remark = url.rsplit('#', 1)  # from right search
    if spaceRemark:  # deal with space remark for space
        remark = remark.replace('+', ' ')
    return url, urlDecode(remark)
