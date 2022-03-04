#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyTester import Xray

testConfig = {}


def loadVlessStream(streamInfo: dict, xtlsFlow: str or None) -> dict:
    proxyInfo = {
        'type': 'vless',
        'server': testConfig['addr'],
        'port': testConfig['port'],
        'id': testConfig['id'],
        'stream': streamInfo['client']
    }
    inboundConfig = {
        'protocol': 'vless',
        'listen': testConfig['bind'],
        'port': testConfig['port'],
        'settings': {
            'clients': [
                {
                    'id': testConfig['id']
                }
            ],
            'decryption': 'none'
        },
        'streamSettings': streamInfo['server']
    }
    if xtlsFlow is not None: # add XTLS flow option
        inboundConfig['settings']['clients'][0]['flow'] = xtlsFlow
    return {
        'caption': 'VLESS network ' + streamInfo['caption'],
        'proxy': proxyInfo,
        'server': {
            'startCommand': ['xray', '-c', testConfig['file']],
            'fileContent': Xray.xrayConfig(inboundConfig),
            'filePath': testConfig['file'],
            'envVar': {}
        },
        'aider': None
    }


def test(config: dict) -> list:
    global testConfig
    testConfig = config
    testList = []

    # TCP stream
    streamInfo = Xray.loadTcpStream(False, '', '')
    testList.append(loadVlessStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVlessStream(streamInfo, None))
    for flow in Xray.xtlsFlowList:
        streamInfo = Xray.loadTcpStream(False, '', '')
        xtlsFlow, streamInfo = Xray.addXtlsConfig(streamInfo, config['cert'], config['key'], config['host'], flow)
        testList.append(loadVlessStream(streamInfo, xtlsFlow))

    streamInfo = Xray.loadTcpStream(True, config['host'], '/')
    testList.append(loadVlessStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVlessStream(streamInfo, None))

    # mKCP stream
    for obfs in Xray.udpObfsList:
        streamInfo = Xray.loadKcpStream(config['passwd'], obfs)
        testList.append(loadVlessStream(streamInfo, None))
        streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
        testList.append(loadVlessStream(streamInfo, None))
        for flow in Xray.xtlsFlowList:
            streamInfo = Xray.loadKcpStream(config['passwd'], obfs)
            xtlsFlow, streamInfo = Xray.addXtlsConfig(streamInfo, config['cert'], config['key'], config['host'], flow)
            testList.append(loadVlessStream(streamInfo, xtlsFlow))

    # WebSocket stream
    streamInfo = Xray.loadWsStream(config['host'], config['path'], False)
    testList.append(loadVlessStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVlessStream(streamInfo, None))

    streamInfo = Xray.loadWsStream(config['host'], config['path'], True)
    testList.append(loadVlessStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVlessStream(streamInfo, None))

    # HTTP/2 stream
    streamInfo = Xray.loadH2Stream(config['host'], config['path'])
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVlessStream(streamInfo, None))

    # QUIC stream
    for method in Xray.quicMethodList:
        for obfs in Xray.udpObfsList:
            streamInfo = Xray.loadQuicStream(method, config['passwd'], obfs)
            streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
            testList.append(loadVlessStream(streamInfo, None))

    # GRPC stream
    streamInfo = Xray.loadGrpcStream(config['service'])
    testList.append(loadVlessStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVlessStream(streamInfo, None))

    streamInfo = Xray.loadGrpcStream(config['service'], multiMode = True)
    testList.append(loadVlessStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadVlessStream(streamInfo, None))

    return testList
