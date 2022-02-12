#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
from ProxyDecoder import baseFunc

def __ssCommonDecode(url: str):
    '''
    Shadowsocks经典分享链接解码

    FORMAT: ss://BASE64-ENCODED-STRING-WITHOUT-PADDING#TAG

    EXAMPLE:
        base64('bf-cfb:test/!@#:@192.168.100.1:8888')
        -> YmYtY2ZiOnRlc3QvIUAjOkAxOTIuMTY4LjEwMC4xOjg4ODg
        -> ss://YmYtY2ZiOnRlc3QvIUAjOkAxOTIuMTY4LjEwMC4xOjg4ODg#example-server
    '''
    content = re.search(r'^ss://([a-zA-Z0-9_=+\\-]+)#?([\S]*)?$', url)
    try:
        info = re.search(
            r'^([\S]+?):([\S]+)@([a-zA-Z0-9.:_-]+):([0-9]+)$',
            baseFunc.base64Decode(content.group(1))
        )
        return {
            'server': info[3],
            'port': int(info[4]),
            'password': info[2],
            'method': info[1],
            'remark': baseFunc.urlDecode(content.group(2))
        }
    except:
        return None

def __sip002Decode(url: str):
    '''
    Shadowsocks SIP002分享链接解码

    FORMAT:
        SS-URI = "ss://" {userinfo} "@" hostname ":" port [ "/" ] [ "?" plugin ] [ "#" tag ]
        userinfo = websafe-base64-encode-utf8(method ":" password)

    EXAMPLE:
        base64('rc4-md5:passwd') -> cmM0LW1kNTpwYXNzd2Q

        obfs-local;obfs=http -> obfs-local%3Bobfs%3Dhttp

        => ss://cmM0LW1kNTpwYXNzd2Q@192.168.100.1:8888/?plugin=obfs-local%3Bobfs%3Dhttp#Example
    '''
    content = re.search(r'^ss://([a-zA-Z0-9_=+\\-]+)@([a-zA-Z0-9.:_-]+):([0-9]+)/?([\S]*)$', url)
    try:
        userInfo = re.search(r'^([\S]+?):([\S]+)$', baseFunc.base64Decode(content.group(1)))
        info = {
            'server': content.group(2),
            'port': int(content.group(3)),
            'password': userInfo.group(2),
            'method': userInfo.group(1)
        }
        if content.group(4).find('#') != -1:
            content = re.search(r'^\??([\S]*)#([\S]*)$', content.group(4))
            remark = content.group(2)
        else:
            content = re.search(r'^\??([\S]*)$', content.group(4))
        for field in content.group(1).split('&'):
            if field.find('=') == -1: continue
            field = re.search(r'^([\S]*)=([\S]*)$', field)
            if field.group(1) == 'plugin':
                plugin = baseFunc.urlDecode(field.group(2))
                break
        plugin = plugin if 'plugin' in dir() else ''
        if plugin.find(';') == -1:
            info['plugin'] = plugin
            info['pluginParam'] = ''
        else:
            plugin = re.search(r'^([\S]*?);([\S]*)$', plugin)
            info['plugin'] = plugin.group(1)
            info['pluginParam'] = plugin.group(2)
        info['remark'] = baseFunc.urlDecode(remark if 'remark' in dir() else '')
        return info
    except:
        return None

def ssDecode(url: str):
    try:
        if url[0:5] != 'ss://':
            return None
        result = __ssCommonDecode(url) # try common decode
        if result != None:
            return result
        result = __sip002Decode(url) # try sip002 decode
        if result != None:
            return result
    except:
        pass
    return None
