#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
from ProxyTester import Xray

testConfig = {}


def trojanBasicTest() -> dict:
    serverConfig = {
        'run_type': 'server',
        'local_addr': testConfig['bind'],
        'local_port': testConfig['port'],
        'password': [
            testConfig['passwd']
        ],
        'ssl': {
            'cert': testConfig['cert'],
            'key': testConfig['key']
        }
    }
    return {
        'caption': 'Trojan basic',
        'proxy': {
            'type': 'trojan',
            'server': testConfig['addr'],
            'port': testConfig['port'],
            'passwd': testConfig['passwd'],
            'stream': {
                'type': 'tcp',
                'secure': {
                    'type': 'tls',
                    'sni': testConfig['host']
                }
            }
        },
        'server': {
            'startCommand': ['trojan', '-c', testConfig['file']],
            'fileContent': json.dumps(serverConfig),
            'filePath': testConfig['file'],
            'envVar': {}
        },
        'aider': None
    }


def loadTrojanStream(streamInfo: dict, xtlsFlow: str or None) -> dict:
    proxyInfo = {
        'type': 'trojan',
        'server': testConfig['addr'],
        'port': testConfig['port'],
        'passwd': testConfig['passwd'],
        'stream': streamInfo['client']
    }
    inboundConfig = {
        'protocol': 'trojan',
        'listen': testConfig['bind'],
        'port': testConfig['port'],
        'settings': {
            'clients': [
                {
                    'password': testConfig['passwd']
                }
            ]
        },
        'streamSettings': streamInfo['server']
    }
    if xtlsFlow is not None: # add XTLS flow option
        inboundConfig['settings']['clients'][0]['flow'] = xtlsFlow
    return {
        'caption': 'Trojan network ' + streamInfo['caption'],
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
    testList = [trojanBasicTest()] # basic test

    # TCP stream
    streamInfo = Xray.loadTcpStream(False, '', '')
    testList.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadTrojanStream(streamInfo, None))
    for flow in Xray.xtlsFlowList:
        streamInfo = Xray.loadTcpStream(False, '', '')
        xtlsFlow, streamInfo = Xray.addXtlsConfig(streamInfo, config['cert'], config['key'], config['host'], flow)
        testList.append(loadTrojanStream(streamInfo, xtlsFlow))

    streamInfo = Xray.loadTcpStream(True, config['host'], '/')
    testList.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadTrojanStream(streamInfo, None))

    # mKCP stream
    for obfs in Xray.udpObfsList:
        streamInfo = Xray.loadKcpStream(config['passwd'], obfs)
        testList.append(loadTrojanStream(streamInfo, None))
        streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
        testList.append(loadTrojanStream(streamInfo, None))
        for flow in Xray.xtlsFlowList:
            streamInfo = Xray.loadKcpStream(config['passwd'], obfs)
            xtlsFlow, streamInfo = Xray.addXtlsConfig(streamInfo, config['cert'], config['key'], config['host'], flow)
            testList.append(loadTrojanStream(streamInfo, xtlsFlow))

    # WebSocket stream
    streamInfo = Xray.loadWsStream(config['host'], config['path'], False)
    testList.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadTrojanStream(streamInfo, None))

    streamInfo = Xray.loadWsStream(config['host'], config['path'], True)
    testList.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadTrojanStream(streamInfo, None))

    # HTTP/2 stream
    streamInfo = Xray.loadH2Stream(config['host'], config['path'])
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadTrojanStream(streamInfo, None))

    # QUIC stream
    for method in Xray.quicMethodList:
        for obfs in Xray.udpObfsList:
            streamInfo = Xray.loadQuicStream(method, config['passwd'], obfs)
            streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
            testList.append(loadTrojanStream(streamInfo, None))

    # GRPC stream
    streamInfo = Xray.loadGrpcStream(config['service'])
    testList.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadTrojanStream(streamInfo, None))

    streamInfo = Xray.loadGrpcStream(config['service'], multiMode = True)
    testList.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    testList.append(loadTrojanStream(streamInfo, None))

    return testList
