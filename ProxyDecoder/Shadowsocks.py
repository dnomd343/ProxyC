#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
from ProxyDecoder import baseFunc

def __ssPlainDecode(url: str) -> dict:
    """
    Shadowsocks原始分享链接解码

    FORMAT: ss://method:password@hostname:port#TAG

    EXAMPLE:
        ss://bf-cfb:test@192.168.100.1:8888#EXAMPLE
    """
    content = re.search(r'^ss://([\s\S]+?)(#[\s\S]*)?$', url) # ...#REMARK
    info = re.search(
        r'^([\S]+?):([\S]+)@([a-zA-Z0-9.:_-]+):([0-9]+)$',
        content.group(1) # method:password@server:port
    )
    remark = content.group(2)[1:] if content.group(2) is not None else ''
    return {
        'server': info[3],
        'port': int(info[4]),
        'passwd': info[2],
        'method': info[1],
        'remark': baseFunc.urlDecode(remark)
    }

def __ssCommonDecode(url: str) -> dict:
    """
    Shadowsocks经典分享链接解码

    FORMAT: ss://BASE64-ENCODED-STRING-WITHOUT-PADDING#TAG

    EXAMPLE:
        base64('bf-cfb:test/!@#:@192.168.100.1:8888')
        -> YmYtY2ZiOnRlc3QvIUAjOkAxOTIuMTY4LjEwMC4xOjg4ODg
        -> ss://YmYtY2ZiOnRlc3QvIUAjOkAxOTIuMTY4LjEwMC4xOjg4ODg#example-server
    """
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

def __sip002Decode(url: str) -> dict:
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
        pluginField = {
            'type': plugin,
            'param': ''
        }
    else: # plugin=...;... (带参数)
        plugin = re.search(r'^([\S]*?);([\S]*)$', plugin) # 插件名;插件参数
        pluginField = {
            'type': plugin.group(1),
            'param': plugin.group(2)
        }
    if pluginField['type'] != '': # 带插件情况
        info['plugin'] = pluginField
    return info

def ssDecode(url: str, compatible: bool = False) -> dict or None:
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
    if url[0:5] != 'ss://':
        return None
    try:
        result = __ssCommonDecode(url) # try shadowsocks common decode
    except:
        try:
            result = __sip002Decode(url)  # try shadowsocks sip002 decode
        except:
            try:
                result = __ssPlainDecode(url)  # try shadowsocks plain decode
            except:
                return None
    if compatible and 'remark' in result: # 向后兼容部分客户端
        result['remark'] = result['remark'].replace('+', ' ')
    result['type'] = 'ss'
    return result
