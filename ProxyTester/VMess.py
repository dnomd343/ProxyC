#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyTester import V2ray

config = {}

vmessMethodList = [
    'aes-128-gcm',
    'chacha20-poly1305',
    'auto',
    'none',
    'zero',
]

def vmessBasicTest(method: str, alterId: int) -> dict:
    inboundConfig = {
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
            'startCommand': ['v2ray', '-c', config['file']],
            'fileContent': V2ray.v2rayConfig(inboundConfig),
            'filePath': config['file'],
            'envVar': envVar
        },
        'aider': None
    }

def loadVmessStream(streamInfo: dict) -> dict:
    proxyInfo = {
        'type': 'vmess',
        'server': '127.0.0.1',
        'port': config['port'],
        'id': config['id'],
        'stream': streamInfo['client']
    }
    inboundConfig = {
        'protocol': 'vmess',
        'listen': '127.0.0.1',
        'port': config['port'],
        'settings': {
            'clients': [
                {
                    'id': config['id']
                }
            ]
        },
        'streamSettings': streamInfo['server']
    }
    return {
        'caption': 'VMess network ' + streamInfo['caption'],
        'proxy': proxyInfo,
        'server': {
            'startCommand': ['v2ray', '-c', config['file']],
            'fileContent': V2ray.v2rayConfig(inboundConfig),
            'filePath': config['file'],
            'envVar': {}
        },
        'aider': None
    }

def vmessTest(vmessConfig: dict) -> list:
    result = []
    for key, value in vmessConfig.items(): # vmessConfig -> config
        config[key] = value

    # Basic test
    for method in vmessMethodList: # methods and AEAD/MD5+AES test
        result.append(vmessBasicTest(method, 0))
        result.append(vmessBasicTest(method, 64))

    # TCP stream
    streamInfo = V2ray.loadTcpStream(False, '', '')
    result.append(loadVmessStream(streamInfo))
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVmessStream(streamInfo))

    streamInfo = V2ray.loadTcpStream(True, config['host'], '/')
    result.append(loadVmessStream(streamInfo))
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVmessStream(streamInfo))

    # mKCP stream
    for obfs in V2ray.udpObfsList:
        streamInfo = V2ray.loadKcpStream(config['passwd'], obfs)
        result.append(loadVmessStream(streamInfo))
        streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
        result.append(loadVmessStream(streamInfo))

    # WebSocket stream
    streamInfo = V2ray.loadWsStream(config['host'], config['path'], False)
    result.append(loadVmessStream(streamInfo))
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVmessStream(streamInfo))

    streamInfo = V2ray.loadWsStream(config['host'], config['path'], True)
    result.append(loadVmessStream(streamInfo))
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVmessStream(streamInfo))

    # HTTP/2 stream
    streamInfo = V2ray.loadH2Stream(config['host'], config['path'])
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVmessStream(streamInfo))

    # QUIC stream
    for method in V2ray.quicMethodList:
        for obfs in V2ray.udpObfsList:
            streamInfo = V2ray.loadQuicStream(method, config['passwd'], obfs)
            streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
            result.append(loadVmessStream(streamInfo))

    # GRPC stream
    streamInfo = V2ray.loadGrpcStream(config['service'])
    result.append(loadVmessStream(streamInfo))
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVmessStream(streamInfo))

    return result
