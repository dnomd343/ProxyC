#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyDecoder import baseFunc


def __addressSplit(address: str) -> dict: # server:port
    if address == '':
        return {}
    server, port = address.rsplit(':', maxsplit = 1)
    return {
        'server': baseFunc.formatHost(server),
        'port': int(port)
    }


def __wsSplit(wsServer: str, params: dict) -> dict: # ws[s]://xxx:xxx/...
    wsUrl = baseFunc.urlSplit(wsServer)
    wsInfo = {
        'server': wsUrl['server'],
        'port': wsUrl['port'],
        'ws': {
            'host': wsUrl['server'],
            'path': wsUrl['path'] if wsUrl['path'] != '' else '/ws' # path as `/ws` when omitted
        }
    }
    if 'address' not in params:
        return wsInfo
    return {
        **wsInfo,
        **__addressSplit(params['address'])  # overwrite server and port
    }


def __brookDecode(url: str) -> dict: # Brook分享链接解码
    """
        Docs: https://txthinking.github.io/brook/#/brook-link
    """
    url = baseFunc.urlSplit(url) # brook://KIND?QUERY
    brookKind = url['server']
    if brookKind not in ['server', 'wsserver', 'wssserver']: # skip socks5
        raise Exception('Unknown brook kind')

    if 'password' not in url['params']:
        raise Exception('Miss password option')
    brookInfo = {
        'passwd': url['params']['password'],
        'remark': url['params']['name'] if 'name' in url['params'] else ''
    }

    if brookKind == 'server': # server mode
        if 'server' not in url['params']:
            raise Exception('Miss server option')
        return {
            **brookInfo,
            **__addressSplit(url['params']['server'])
        }

    if brookKind == 'wsserver': # ws server mode
        if 'wsserver' not in url['params']:
            raise Exception('Miss wsserver option')
        return {
            **brookInfo,
            **__wsSplit(url['params']['wsserver'], url['params'])
        }

    if brookKind == 'wssserver': # wss server mode
        if 'wssserver' not in url['params']:
            raise Exception('Miss wssserver option')
        brookInfo = {
            **brookInfo,
            **__wsSplit(url['params']['wssserver'], url['params'])
        }
        brookInfo['ws']['secure'] = {}
        if 'insecure' in url['params'] and url['params']['insecure'] == 'true':
            brookInfo['ws']['secure']['verify'] = False
        return brookInfo


def decode(url: str) -> dict:
    if url.split('://')[0] != 'brook':
        raise Exception('Unexpected scheme')
    return {
        **{'type': 'brook'},
        **__brookDecode(url)
    }
