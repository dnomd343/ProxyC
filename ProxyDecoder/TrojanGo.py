#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
from ProxyDecoder import baseFunc

def __trojanGoCommonDecode(url: str) -> dict:
    """
    Trojan-Go标准分享链接解码

    FORMAT: trojan-go://$(password)@server:port/?{fields}#$(remark)

        sni -> TLS SNI

        type -> original / ws

        host -> WebSocket Host

        path -> WebSocket Path

        encryption -> urlEncode(ss;aes-256-gcm;ss-password)

        plugin -> urlEncode(pluginName;pluginOption) -> officially undefined (refer to SIP002 scheme)

    """
    match = re.search(r'^trojan-go://([\S]+?)(#[\S]*)?$', url) # trojan-go://...#REMARK
    remark = baseFunc.urlDecode(
        match[2][1:] if match[2] is not None else ''
    )
    match = re.search(
        r'^([\S]+)@([a-zA-Z0-9.:\-_\[\]]+)/?([\S]*)$', match[1] # $(password)@server[:port]/?...
    )
    info = {
        'passwd': baseFunc.urlDecode(match[1]),
        'remark': remark
    }
    params = baseFunc.paramSplit(match[3])
    match = re.search(
        r'^([a-zA-Z0-9.:\-_\[\]]+?)(:([0-9]{1,5}))?$', match[2] # server[:port]
    )
    info['server'] = baseFunc.formatHost(match[1])
    info['port'] = int(match[3]) if match[3] is not None else 443

    if 'sni' in params:
        info['sni'] = params['sni']

    if 'type' in params:
        if params['type'] not in ['', 'original', 'ws']:
            raise Exception('Unknown Trojan-Go network type')
        if params['type'] == 'ws': # WebSocket mode
            info['ws'] = {}
            if 'host' in params:
                info['ws']['host'] = params['host']
            if 'path' in params:
                info['ws']['path'] = params['path']

    if 'encryption' in params and params['encryption'] not in ['', 'none']: # shadowsocks encrypt
        match = re.search(
            r'^ss;([a-zA-Z0-9\-_]+):([\S]+)$', params['encryption']
        )
        info['ss'] = {
            'method': match[1],
            'passwd': match[2]
        }

    if 'plugin' in params and params['plugin'] not in ['', 'none']: # SIP003 plugin
        match = re.search(
            r'^([\S]+?)(;([\S]+))?$', params['plugin']
        )
        info['plugin'] = {
            'type': match[1],
            'param': match[3] if match[3] is not None else ''
        }
    return info

def trojanGoDecode(url: str) -> dict or None:
    """
    Trojan-Go分享链接解码

        链接合法:
            return {
                'type': 'trojan-go',
                ...
            }

        链接不合法:
            return None
    """
    if url[0:12] != 'trojan-go://':
        return None
    try:
        result = __trojanGoCommonDecode(url)  # try Trojan-Go common decode
    except:
        return None
    result['type'] = 'trojan-go'
    return result
