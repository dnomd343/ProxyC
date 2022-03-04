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
    remark = ''
    match = re.search(r'^ss://([\S]+)$', url) # ss://...
    if match[1].find('#') != -1: # ...#REMARK
        match = re.search(r'^([\S]+)#([\S]*)$', match[1])
        remark = baseFunc.urlDecode(
            match[2] if match[2] is not None else ''
        )
    match = re.search(
        r'^([\S]+?):([\S]+)@([a-zA-Z0-9.:\-_\[\]]+):([0-9]+)$', match[1] # method:password@server:port
    )
    return {
        'server': baseFunc.formatHost(match[3]),
        'port': int(match[4]),
        'passwd': match[2],
        'method': match[1],
        'remark': remark
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
    match = re.search(r'^ss://([a-zA-Z0-9\-_+\\=]+)#?([\S]*)?$', url)  # base64#REMARK
    remark = baseFunc.urlDecode(
        match[2] if match[2] is not None else ''
    )
    match = re.search(
        r'^([\S]+?):([\S]+)@([a-zA-Z0-9.:\-_\[\]]+):([0-9]+)$',
        baseFunc.base64Decode(match[1]) # method:password@server:port
    )
    return {
        'server': baseFunc.formatHost(match[3]),
        'port': int(match[4]),
        'passwd': match[2],
        'method': match[1],
        'remark': remark
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
    match = re.search(
        r'^ss://([a-zA-Z0-9\-_+\\=]+)@([a-zA-Z0-9.:\-_\[\]]+):([0-9]+)'
        r'/?([\S]*)$', url  # base64@server:port/... (/可选)
    )
    userInfo = re.search(
        r'^([\S]+?):([\S]+)$',
        baseFunc.base64Decode(match[1]) # method:password
    )

    info = {
        'server': baseFunc.formatHost(match[2]),
        'port': int(match[3]),
        'passwd': userInfo[2],
        'method': userInfo[1],
        'remark': ''
    }
    if match[4].find('#') != -1: # ...#REMARK
        match = re.search(
            r'^\??([\S]*)#([\S]*)$', match[4] # ?...#REMARK (?可选)
        )
        info['remark'] = baseFunc.urlDecode(match[2])
    else:
        match = re.search(
            r'^\??([\S]*)$', match[4] # ?... (?可选)
        )

    params = baseFunc.paramSplit(match[1]) # /?plugin=...&other1=...&other2=...
    pluginField = params['plugin'] if 'plugin' in params else ''
    if pluginField.find(';') == -1: # plugin=... (无参数)
        pluginObject = {
            'type': pluginField,
            'param': ''
        }
    else: # plugin=...;... (带参数)
        match = re.search(r'^([\S]*?);([\S]*)$', pluginField) # 插件名;插件参数
        pluginObject = {
            'type': match[1],
            'param': match[2]
        }
    if pluginObject['type'] != '': # 带插件时配置
        info['plugin'] = pluginObject
    return info


def decode(url: str, compatible: bool = False) -> dict or None:
    if url.split('://')[0] != 'ss':
        raise Exception('Unexpected scheme')
    try:
        ssInfo = __ssCommonDecode(url) # try shadowsocks common decode
    except:
        try:
            ssInfo = __sip002Decode(url)  # try shadowsocks sip002 decode
        except:
            try:
                ssInfo = __ssPlainDecode(url)  # try shadowsocks plain decode
            except:
                raise Exception('Url could not be parsed')

    if compatible and 'remark' in ssInfo: # 向后兼容部分客户端
        ssInfo['remark'] = ssInfo['remark'].replace('+', ' ')
    return {
        **{'type': 'ss'},
        **ssInfo
    }
