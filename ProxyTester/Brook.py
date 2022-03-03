#!/usr/bin/python
# -*- coding:utf-8 -*-

testConfig = {}

def __originConfig() -> dict:
    return {
        'caption': 'Brook original',
        'client': {
            'type': 'brook',
            'server': testConfig['host'],
            'port': testConfig['port'],
            'passwd': testConfig['passwd']
        },
        'server': [
            'brook', 'server',
            '--listen', testConfig['bind'] + ':' + str(testConfig['port']),
            '--password', testConfig['passwd']
        ]
    }


def __wsConfig() -> dict:
    return {
        'caption': 'Brook websocket',
        'client': {
            'type': 'brook',
            'server': testConfig['host'],
            'port': testConfig['port'],
            'passwd': testConfig['passwd'],
            'ws': {
                'host': testConfig['host'],
                'path': testConfig['path']
            }
        },
        'server': [
            'brook', 'wsserver',
            '--listen', testConfig['bind'] + ':' + str(testConfig['port']),
            '--password', testConfig['passwd'],
            '--path', testConfig['path']
        ]
    }


def __wssConfig() -> dict:
    return {
        'caption': 'Brook websocket with TLS',
        'client': {
            'type': 'brook',
            'server': testConfig['host'],
            'port': testConfig['port'],
            'passwd': testConfig['passwd'],
            'ws': {
                'host': testConfig['host'],
                'path': testConfig['path'],
                'secure': {
                    'verify': True
                }
            }
        },
        'server': [
            'brook', 'wssserver',
            '--domainaddress', testConfig['host'] + ':' + str(testConfig['port']),
            '--cert', testConfig['cert'],
            '--certkey', testConfig['key'],
            '--password', testConfig['passwd'],
            '--path', testConfig['path']
        ]
    }


def __brookConfig(brookConfig: dict) -> dict:
    return {
        'caption': brookConfig['caption'],
        'proxy': brookConfig['client'],
        'server': {
            'startCommand': brookConfig['server'],
            'fileContent': None,
            'filePath': None,
            'envVar': {}
        },
        'aider': None
    }


def test(config: dict) -> list:
    global testConfig
    testConfig = config
    return [
        __brookConfig(__originConfig()),
        __brookConfig(__wsConfig()),
        __brookConfig(__wssConfig()),
    ]
