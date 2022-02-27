#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import json
from ProxyDecoder import baseFunc

def __splitEdParam(path: str) -> tuple[int or None, str]: # 分离early-data参数
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

def __vmessV2raynDecode(url: str) -> dict:
    """
    v2rayN / v2rayNG分享链接解码

    FORMAT: vmess://BASE64-ENCODED-JSON-STRING

        {
          "v": "2",
          "ps": "...",
          "add": "...",
          "port": "...",
          "id": "...",
          "aid": "...",
          "scy": "...",
          "net": "...",
          "type": "...",
          "host": "...",
          "path": "...",
          "tls": "...",
          "sni": "...",
          "alpn": "..."
        }
    """
    content = json.loads(
        baseFunc.base64Decode(
            re.search(r'^vmess://([\S]+)$', url).group(1) # vmess://{base64}
        )
    )
    if int(content['v']) != 2: # version => 2
        raise Exception('Unknown version field')
    info = {
        'server': content['add'],
        'port': int(content['port']),
        'id': content['id'],
        'aid': int(content['aid']),
    }
    if 'ps' in content: # ps -> remark
        info['remark'] = content['ps']
    if 'scy' in content: # scy -> method
        info['method'] = content['scy']
    stream = {
        'type': content['net'] # net -> stream.type
    }
    if content['net'] == 'tcp':
        if 'http' in content and content['type'] == 'http': # type -> none / http
            stream['obfs'] = {
                'host': content['host'],
                'path': content['path']
            }
    elif content['net'] == 'kcp':
        if 'type' in content:
            stream['obfs'] = content['type']
        if 'path' in content:
            stream['seed'] = content['path'] # path -> seed
    elif content['net'] == 'ws':
        if 'host' in content:
            stream['host'] = content['host']
        if 'path' in content:
            try:
                stream['ed'], stream['path'] = __splitEdParam(content['path'])
            except:
                stream['path'] = content['path']
    elif content['net'] == 'h2':
        if 'host' in content:
            stream['host'] = content['host']
        if 'path' in content:
            stream['path'] = content['path']
    elif content['net'] == 'quic':
        if 'type' in content:
            stream['obfs'] = content['type']
        if 'host' in content:
            stream['method'] = content['host']
        if 'path' in content:
            stream['passwd'] = content['path']
    elif content['net'] == 'grpc':
        if 'type' in content and content['type'] == 'multi':
            stream['mode'] = 'multi'
        if 'path' in content:
            stream['service'] = content['path']
    else:
        raise Exception('Unknown network type')

    secure = None
    if 'tls' in content and content['tls'] == 'tls': # enable TLS
        secure = {}
        if 'sni' in content:
            secure['sni'] = content['sni'] # sni option
        if 'alpn' in content:
            if content['alpn'] == '':
                secure['alpn'] = None # ignore alpn option
            else:
                secure['alpn'] = content['alpn'] # h2 | http/1.1 | h2,http/1.1

    stream['secure'] = secure
    info['stream'] = stream
    return info

def vmessDecode(url: str) -> dict or None:
    """
    VMess分享链接解码

        链接合法:
            return {
                'type': 'vmess',
                ...
            }

        链接不合法:
            return None
    """
    if url[0:8] != 'vmess://':
        return None
    try:
        result = __vmessV2raynDecode(url) # try v2rayN decode
    except:
        return None
    result['type'] = 'vmess'
    return result
