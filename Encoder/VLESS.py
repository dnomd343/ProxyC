#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Utils.Common import urlEncode

def vless(info: dict, name: str) -> str:
    """
    https://github.com/XTLS/Xray-core/discussions/716
    
    FORMAT: protocol://$(uuid)@remote-host:remote-port?<protocol-specific fields><transport-specific fields><tls-specific fields>#$(descriptive-text)
    """
    
    link = 'vless://'
    link += info['id'] + '@' # add <uuid>
    link += info['server'] + ':' # add <remote-host>
    link += str(info['port']) + '?' # add <remote-port>
    
    # stream settings
    streamInfo = info['stream']
    
    stremType = streamInfo['type']
    flow = streamInfo.get('flow', None)
    headerType = streamInfo.get('obfs', 'none')
    host = streamInfo['secure'].get('host', None)
    path = streamInfo['secure'].get('path', None)
    alpn = streamInfo['secure'].get('alpn', None)
    sni = streamInfo['secure'].get('sni', None)
    security = streamInfo['secure'].get('type', None)
    
    link += 'type=' + stremType + '&' # add <type>
    link += 'flow=' + flow + '&' if flow else '' # add <flow>
    link += 'headerType=' + headerType + '&' if headerType != None else 'none' # add <headerType>
    link += 'security=' + security + '&' if security else '' # add <security>
    link += 'alpn=' + alpn + '&' if alpn else '' # add <alpn>
    link += 'sni=' + sni + '&' if sni else '' # add <sni>
    link += 'host=' + host + '&' if host else '' # add <host>
    link += 'path=' + path + '&' if path else '' # add <path>

    link += '#' + urlEncode(name) # add <descriptive-text>
    return link