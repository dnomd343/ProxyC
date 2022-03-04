#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyTester import V2ray

testConfig = {}

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
        'listen': testConfig['bind'],
        'port': testConfig['port'],
        'settings': {
            'clients': [
                {
                    'id': testConfig['id'],
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
            'server': testConfig['addr'],
            'port': testConfig['port'],
            'method': method,
            'id': testConfig['id'],
            'aid': alterId
        },
        'server': {
            'startCommand': ['v2ray', '-c', testConfig['file']],
            'fileContent': V2ray.v2rayConfig(inboundConfig),
            'filePath': testConfig['file'],
            'envVar': envVar
        },
        'aider': None
    }

def loadVmessStream(streamInfo: dict) -> dict:
    proxyInfo = {
        'type': 'vmess',
        'server': testConfig['addr'],
        'port': testConfig['port'],
        'id': testConfig['id'],
        'stream': streamInfo['client']
    }
    inboundConfig = {
        'protocol': 'vmess',
        'listen': testConfig['bind'],
        'port': testConfig['port'],
        'settings': {
            'clients': [
                {
                    'id': testConfig['id']
                }
            ]
        },
        'streamSettings': streamInfo['server']
    }
    return {
        'caption': 'VMess network ' + streamInfo['caption'],
        'proxy': proxyInfo,
        'server': {
            'startCommand': ['v2ray', '-c', testConfig['file']],
            'fileContent': V2ray.v2rayConfig(inboundConfig),
            'filePath': testConfig['file'],
            'envVar': {}
        },
        'aider': None
    }

def test(config: dict) -> list:
    global testConfig
    testConfig = config
    testList = []

    # Basic test
    for method in vmessMethodList: # methods and AEAD/MD5+AES test
        testList.append(vmessBasicTest(method, 0))
        testList.append(vmessBasicTest(method, 64))

    # TCP stream
    streamInfo = V2ray.loadTcpStream(False, '', '')
    testList.append(loadVmessStream(streamInfo))
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVmessStream(streamInfo))

    streamInfo = V2ray.loadTcpStream(True, config['host'], '/')
    testList.append(loadVmessStream(streamInfo))
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVmessStream(streamInfo))

    # mKCP stream
    for obfs in V2ray.udpObfsList:
        streamInfo = V2ray.loadKcpStream(config['passwd'], obfs)
        testList.append(loadVmessStream(streamInfo))
        streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
        testList.append(loadVmessStream(streamInfo))

    # WebSocket stream
    streamInfo = V2ray.loadWsStream(config['host'], config['path'], False)
    testList.append(loadVmessStream(streamInfo))
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVmessStream(streamInfo))

    streamInfo = V2ray.loadWsStream(config['host'], config['path'], True)
    testList.append(loadVmessStream(streamInfo))
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVmessStream(streamInfo))

    # HTTP/2 stream
    streamInfo = V2ray.loadH2Stream(config['host'], config['path'])
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVmessStream(streamInfo))

    # QUIC stream
    for method in V2ray.quicMethodList:
        for obfs in V2ray.udpObfsList:
            streamInfo = V2ray.loadQuicStream(method, config['passwd'], obfs)
            streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
            testList.append(loadVmessStream(streamInfo))

    # GRPC stream
    streamInfo = V2ray.loadGrpcStream(config['service'])
    testList.append(loadVmessStream(streamInfo))
    streamInfo = V2ray.addSecureConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVmessStream(streamInfo))

    return testList
