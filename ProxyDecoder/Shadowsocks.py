#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
from ProxyDecoder import baseFunc

def __ssPlainDecode(url: str) -> dict or None:
    """
    Shadowsocks原始分享链接解码

    FORMAT: ss://method:password@hostname:port#TAG

    EXAMPLE:
        ss://bf-cfb:test@192.168.100.1:8888#EXAMPLE
    """
    try:
        content = re.search(r'^ss://([\s\S]+?)(#[\s\S]*)?$', url) # ...#REMARK
        info = re.search(
            r'^([\S]+?):([\S]+)@([a-zA-Z0-9.:_-]+):([0-9]+)$',
            content.group(1) # method:password@server:port
        )
        remark = content.group(2)[1:] if content.group(2) is not None else ''
        remark = remark.replace('+', ' ') # 向后兼容部分客户端
        return {
            'server': info[3],
            'port': int(info[4]),
            'passwd': info[2],
            'method': info[1],
            'remark': baseFunc.urlDecode(remark)
        }
    except:
        return None

def __ssCommonDecode(url: str) -> dict or None:
    """
    Shadowsocks经典分享链接解码

    FORMAT: ss://BASE64-ENCODED-STRING-WITHOUT-PADDING#TAG

    EXAMPLE:
        base64('bf-cfb:test/!@#:@192.168.100.1:8888')
        -> YmYtY2ZiOnRlc3QvIUAjOkAxOTIuMTY4LjEwMC4xOjg4ODg
        -> ss://YmYtY2ZiOnRlc3QvIUAjOkAxOTIuMTY4LjEwMC4xOjg4ODg#example-server
    """
    try:
        content = re.search(r'^ss://([a-zA-Z0-9_=+\\-]+)#?([\S]*)?$', url)  # base64#REMARK
        info = re.search(
            r'^([\S]+?):([\S]+)@([a-zA-Z0-9.:_-]+):([0-9]+)$',
            baseFunc.base64Decode(content.group(1)) # method:password@server:port
        )
        return {
            'server': info[3],
            'port': int(info[4]),
            'passwd': info[2],
            'method': info[1],
            'remark': baseFunc.urlDecode(content.group(2))
        }
    except:
        return None

def __sip002Decode(url: str) -> dict or None:
    """
    Shadowsocks SIP002分享链接解码

    FORMAT:
        SS-URI = "ss://" {userinfo} "@" hostname ":" port [ "/" ] [ "?" plugin ] [ "#" tag ]
        userinfo = websafe-base64-encode-utf8(method ":" password)

    EXAMPLE:
        base64('rc4-md5:passwd') -> cmM0LW1kNTpwYXNzd2Q

        obfs-local;obfs=http -> obfs-local%3Bobfs%3Dhttp

        => ss://cmM0LW1kNTpwYXNzd2Q@192.168.100.1:8888/?plugin=obfs-local%3Bobfs%3Dhttp#Example
    """
    try:
        content = re.search(
            r'^ss://([a-zA-Z0-9_=+\\-]+)@([a-zA-Z0-9.:_-]+):([0-9]+)'
            r'/?([\S]*)$', url  # base64@server:port/... (/可选)
        )
        userInfo = re.search(
            r'^([\S]+?):([\S]+)$',
            baseFunc.base64Decode(content.group(1)) # method:password
        )
        info = {
            'server': content.group(2),
            'port': int(content.group(3)),
            'passwd': userInfo.group(2),
            'method': userInfo.group(1),
            'remark': ''
        }
        if content.group(4).find('#') != -1: # ...#REMARK
            content = re.search(
                r'^\??([\S]*)#([\S]*)$',
                content.group(4) # ?...#REMARK (?可选)
            )
            info['remark'] = baseFunc.urlDecode(
                content.group(2)
            )
        else:
            content = re.search(
                r'^\??([\S]*)$',
                content.group(4) # ?... (?可选)
            )
        plugin = ''
        for field in content.group(1).split('&'): # /?plugin=...&other1=...&other2=...
            if field.find('=') == -1: # 缺失xxx=...
                continue
            field = re.search(r'^([\S]*?)=([\S]*)$', field) # xxx=...
            if field.group(1) == 'plugin':
                plugin = baseFunc.urlDecode(field.group(2)) # plugin参数
                break
        if plugin.find(';') == -1: # plugin=... (无参数)
            info['plugin'] = {
                'type': plugin,
                'param': ''
            }
        else: # plugin=...;... (带参数)
            plugin = re.search(r'^([\S]*?);([\S]*)$', plugin) # 插件名;插件参数
            info['plugin'] = {
                'type': plugin.group(1),
                'param': plugin.group(2)
            }
        return info
    except:
        return None

def ssDecode(url: str) -> dict or None:
    """
    Shadowsocks分享链接解码

        链接合法:
            return {
                'type': 'ss',
                ...
            }

        链接不合法:
            return None
    """
    try:
        if url[0:5] != 'ss://':
            return None
        result = __ssCommonDecode(url) # try shadowsocks common decode
        if result is None:
            result = __sip002Decode(url) # try shadowsocks sip002 decode
        if result is None:
            result = __ssPlainDecode(url) # try shadowsocks plain decode
        if result is not None: # 解析成功
            result['type'] = 'ss'
            return result
    except:
        pass
    return None
