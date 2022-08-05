#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Filter.Plugin import pluginFormat
from Basis.Functions import toInt, toStr
from Basis.Functions import isHost, isPort
from Basis.Constant import ssMethods, pluginClients

pluginObject = {
    'type': {
        'type': str,
        'format': lambda s: pluginFormat(toStr(s).strip().lower()),
        'filter': lambda s: s in pluginClients,
        'errMsg': 'Unknown SIP003 plugin'
    },
    'param': {
        'optional': False,
        'default': '',
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid SIP003 param'
    }
}

ssObject = {
    'server': {
        'type': str,
        'format': toStr,
        'filter': isHost,
        'errMsg': 'Invalid server address'
    },
    'port': {
        'type': int,
        'format': toInt,
        'filter': isPort,
        'errMsg': 'Invalid port number'
    },
    'method': {
        'type': str,
        'format': lambda s: toStr(s).strip().lower().replace('_', '-'),
        'filter': lambda s: s in ssMethods,
        'errMsg': 'Unknown Shadowsocks method'
    },
    'passwd': {
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid password content'
    },
    'plugin': {
        'optional': False,
        'default': None,
        'allowNone': True,
        'type': pluginObject,
        'errMsg': 'Invalid pluginObject'
    }
}
