#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Utils.Common import isHost, isPort
from Utils.Filter import Filter, rulesFilter
from Utils.Common import toInt, toStr, toStrTidy, toBool

secureObject = rulesFilter({
    'verify': {
        'optional': True,
        'default': True,
        'type': bool,
        'format': toBool,
        'errMsg': 'Invalid verify option'
    }
})

originObject = rulesFilter({
    'type': {
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s == 'origin',
        'errMsg': 'Invalid Origin stream type'
    },
    'uot': {
        'optional': True,
        'default': False,
        'type': bool,
        'format': toBool,
        'errMsg': 'Invalid UoT option'
    }
})

wsObject = rulesFilter({
    'type': {
        'type': str,
        'format': toStrTidy,
        'filter': lambda s: s == 'ws',
        'errMsg': 'Invalid WebSocket stream type'
    },
    'host': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStrTidy,
        'errMsg': 'Invalid WebSocket host'
    },
    'path': {
        'optional': True,
        'default': '/ws',
        'type': str,
        'format': lambda s: toStr(s).strip(),
        'errMsg': 'Invalid WebSocket path'
    },
    'raw': {
        'optional': True,
        'default': False,
        'type': bool,
        'format': toBool,
        'errMsg': 'Invalid raw option'
    },
    'secure': {
        'optional': True,
        'default': None,
        'allowNone': True,
        'type': secureObject,
        'errMsg': 'Invalid secure options'
    }
})

brookObject = rulesFilter({
    'server': {
        'type': str,
        'format': toStrTidy,
        'filter': isHost,
        'errMsg': 'Invalid server address'
    },
    'port': {
        'type': int,
        'format': toInt,
        'filter': isPort,
        'errMsg': 'Invalid port number'
    },
    'passwd': {
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid password content'
    },
    'stream': {
        'optional': True,
        'default': {
            'type': 'origin'
        },
        'multiSub': True,
        'type': {
            'origin': originObject,
            'ws': wsObject,
        },
        'errMsg': 'Invalid Brook stream'
    }
})


def brookFilter(proxyInfo: dict) -> dict:
    proxyInfo = copy.deepcopy(proxyInfo)
    proxyInfo = Filter(proxyInfo, brookObject)  # run filter
    stream = proxyInfo['stream']
    if stream['type'] == 'ws' and stream['host'] == '':
        stream['host'] = proxyInfo['server']  # fill host option in WebSocket stream
    return proxyInfo
