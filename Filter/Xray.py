#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Filter import V2ray
from Utils.Filter import rulesFilter
from Utils.Constant import xtlsFlows
from Utils.Common import toStrTidy, toBool


def xtlsFlowFormat(flow: str) -> str:
    flow = flow.replace('_', '-')
    xtlsFlowAlias = {
        'xtls-origin': {'origin', 'xtls-rprx-origin'},
        'xtls-direct': {'direct', 'xtls-rprx-direct'},
        'xtls-splice': {'splice', 'xtls-rprx-splice'},
    }
    for xtlsFlow, alias in xtlsFlowAlias.items():
        if flow in alias:
            return xtlsFlow
    return flow  # alias not found


tlsObject = rulesFilter({
    'type': {
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s == 'tls',
        'errMsg': 'Invalid TLS secure type'
    },
    'sni': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStrTidy,
        'errMsg': 'Invalid SNI content'
    },
    'alpn': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': str,
        'format': lambda s: toStrTidy(s).replace(' ', ''),  # remove space
        'filter': lambda s: s in ['h2', 'http/1.1', 'h2,http/1.1'],
        'errMsg': 'Invalid alpn option'
    },
    'verify': {
        'optional': True,
        'default': True,
        'type': bool,
        'format': toBool,
        'errMsg': 'Invalid verify option'
    }
})

xtlsObject = rulesFilter({
    'type': {
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s == 'xtls',
        'errMsg': 'Invalid XTLS secure type'
    },
    'sni': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStrTidy,
        'errMsg': 'Invalid SNI content'
    },
    'alpn': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': str,
        'format': lambda s: toStrTidy(s).replace(' ', ''),  # remove space
        'filter': lambda s: s in ['h2', 'http/1.1', 'h2,http/1.1'],
        'errMsg': 'Invalid alpn option'
    },
    'verify': {
        'optional': True,
        'default': True,
        'type': bool,
        'format': toBool,
        'errMsg': 'Invalid verify option'
    },
    'flow': {
        'optional': True,
        'default': 'xtls-direct',
        'type': str,
        'format': lambda s: xtlsFlowFormat(toStrTidy(s)),
        'filter': lambda s: s in xtlsFlows,
        'errMsg': 'Unknown XTLS flow'
    },
    'udp443': {
        'optional': True,
        'default': False,
        'type': bool,
        'format': toBool,
        'errMsg': 'Invalid udp/443 option'
    }
})

secureRule_1 = {  # None / tlsObject / xtlsObject
    'optional': True,
    'default': {
        'type': 'tls'
    },
    'allowNone': True,
    'multiSub': True,
    'type': {
        'tls': tlsObject,
        'xtls': xtlsObject,
    },
    'errMsg': 'Invalid secure options'
}

secureRule_2 = {  # None / tlsObject
    'optional': True,
    'default': {
        'type': 'tls'
    },
    'allowNone': True,
    'type': tlsObject,
    'errMsg': 'Invalid secure options'
}

secureRule_3 = {  # tlsObject
    'optional': True,
    'default': {
        'type': 'tls'
    },
    'type': tlsObject,
    'errMsg': 'Invalid secure options'
}

tcpObject = rulesFilter({
    **copy.deepcopy(V2ray.tcpObject),
    'secure': secureRule_1  # None / tlsObject / xtlsObject
})

kcpObject = rulesFilter({
    **copy.deepcopy(V2ray.kcpObject),
    'secure': secureRule_1  # None / tlsObject / xtlsObject
})

wsObject = rulesFilter({
    **copy.deepcopy(V2ray.wsObject),
    'secure': secureRule_2  # None / tlsObject
})

h2Object = rulesFilter({
    **copy.deepcopy(V2ray.h2Object),
    'secure': secureRule_3  # tlsObject
})

quicObject = rulesFilter({
    **copy.deepcopy(V2ray.quicObject),
    'secure': secureRule_3  # tlsObject
})

grpcObject = rulesFilter({
    **copy.deepcopy(V2ray.grpcObject),
    'secure': secureRule_2  # None / tlsObject
})

addSni = V2ray.addSni
