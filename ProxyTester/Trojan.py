#!/usr/bin/python
# -*- coding:utf-8 -*-
import json

from ProxyTester import Xray

config = {}

def trojanBasicTest() -> dict:
    serverConfig = {
        'run_type': 'server',
        'local_addr': '127.0.0.1',
        'local_port': config['port'],
        'password': [
            config['passwd']
        ],
        'ssl': {
            'cert': config['cert'],
            'key': config['key']
        }
    }
    return {
        'caption': 'Trojan basic',
        'proxy': {
            'type': 'trojan',
            'server': '127.0.0.1',
            'port': config['port'],
            'passwd': config['passwd'],
            'stream': {
                'type': 'tcp',
                'secure': {
                    'type': 'tls',
                    'sni': config['host']
                }
            }
        },
        'server': {
            'startCommand': ['trojan', '-c', config['file']],
            'fileContent': json.dumps(serverConfig),
            'filePath': config['file'],
            'envVar': {}
        },
        'aider': None
    }

def loadTrojanStream(streamInfo: dict, xtlsFlow: str or None) -> dict:
    proxyInfo = {
        'type': 'trojan',
        'server': '127.0.0.1',
        'port': config['port'],
        'passwd': config['passwd'],
        'stream': streamInfo['client']
    }
    inboundConfig = {
        'protocol': 'trojan',
        'listen': '127.0.0.1',
        'port': config['port'],
        'settings': {
            'clients': [
                {
                    'password': config['passwd']
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
            'startCommand': ['xray', '-c', config['file']],
            'fileContent': Xray.xrayConfig(inboundConfig),
            'filePath': config['file'],
            'envVar': {}
        },
        'aider': None
    }

def trojanTest(trojanConfig: dict) -> list:
    result = []
    for key, value in trojanConfig.items(): # trojanConfig -> config
        config[key] = value

    result.append(trojanBasicTest()) # basic test

    # TCP stream
    streamInfo = Xray.loadTcpStream(False, '', '')
    result.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadTrojanStream(streamInfo, None))
    for flow in Xray.xtlsFlowList:
        streamInfo = Xray.loadTcpStream(False, '', '')
        xtlsFlow, streamInfo = Xray.addXtlsConfig(streamInfo, config['cert'], config['key'], config['host'], flow)
        result.append(loadTrojanStream(streamInfo, xtlsFlow))

    streamInfo = Xray.loadTcpStream(True, config['host'], '/')
    result.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadTrojanStream(streamInfo, None))

    # mKCP stream
    for obfs in Xray.udpObfsList:
        streamInfo = Xray.loadKcpStream(config['passwd'], obfs)
        result.append(loadTrojanStream(streamInfo, None))
        streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
        result.append(loadTrojanStream(streamInfo, None))
        for flow in Xray.xtlsFlowList:
            streamInfo = Xray.loadKcpStream(config['passwd'], obfs)
            xtlsFlow, streamInfo = Xray.addXtlsConfig(streamInfo, config['cert'], config['key'], config['host'], flow)
            result.append(loadTrojanStream(streamInfo, xtlsFlow))

    # WebSocket stream
    streamInfo = Xray.loadWsStream(config['host'], config['path'], False)
    result.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadTrojanStream(streamInfo, None))

    streamInfo = Xray.loadWsStream(config['host'], config['path'], True)
    result.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadTrojanStream(streamInfo, None))

    # HTTP/2 stream
    streamInfo = Xray.loadH2Stream(config['host'], config['path'])
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadTrojanStream(streamInfo, None))

    # QUIC stream
    for method in Xray.quicMethodList:
        for obfs in Xray.udpObfsList:
            streamInfo = Xray.loadQuicStream(method, config['passwd'], obfs)
            streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
            result.append(loadTrojanStream(streamInfo, None))

    # GRPC stream
    streamInfo = Xray.loadGrpcStream(config['service'])
    result.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadTrojanStream(streamInfo, None))

    streamInfo = Xray.loadGrpcStream(config['service'], multiMode = True)
    result.append(loadTrojanStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadTrojanStream(streamInfo, None))

    return result
