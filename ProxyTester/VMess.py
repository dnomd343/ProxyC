#!/usr/bin/python
# -*- coding:utf-8 -*-

import copy
import json

config = {}

vmessMethodList = [
    'aes-128-gcm',
    'chacha20-poly1305',
    'auto',
    'none',
    'zero',
]

def loadServerConfig(inboundObject: dict) -> str:
    return json.dumps({
        'log': {
            'loglevel': 'warning'
        },
        'inbounds': [inboundObject],
        'outbounds': [
            {
                'protocol': 'freedom'
            }
        ]
    })

def basicConfig(method: str, alterId: int):
    filePath = '/tmp/v2ray.json'

    inboundObject = {
        'protocol': 'vmess',
        'listen': '127.0.0.1',
        'port': config['port'],
        'settings': {
            'clients': [
                {
                    'id': config['id'],
                    'alterId': alterId
                }
            ]
        }
    }

    caption = 'VMess method ' + method
    if alterId == 0:
        envVar = {}
        caption += ' (AEAD)'
    else:
        envVar = {
            'v2ray.vmess.aead.forced': 'false'
        }
        caption += ' (alterId ' + str(alterId) + ')'

    return {
        'caption': caption,
        'proxy': {
            'type': 'vmess',
            'server': '127.0.0.1',
            'port': config['port'],
            'method': method,
            'id': config['id'],
            'aid': alterId
        },
        'server': {
            'startCommand': ['v2ray', '-c', filePath],
            'fileContent': loadServerConfig(inboundObject),
            'filePath': filePath,
            'envVar': envVar
        },
        'aider': None
    }

def vmessTest(vmessConfig: dict) -> list:
    result = []
    for key, value in vmessConfig.items(): # vmessConfig -> config
        config[key] = value
    for method in vmessMethodList: # methods and AEAD/MD5+AES test
        result.append(basicConfig(method, 0))
        result.append(basicConfig(method, 64))

    return result
