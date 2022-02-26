#!/usr/bin/python
# -*- coding:utf-8 -*-

from ProxyTester import Xray

config = {}

def loadVlessStream(streamInfo: dict, xtlsFlow: str or None) -> dict:
    proxyInfo = {
        'type': 'vless',
        'server': '127.0.0.1',
        'port': config['port'],
        'id': config['id'],
        'stream': streamInfo['client']
    }
    inboundConfig = {
        'protocol': 'vless',
        'listen': '127.0.0.1',
        'port': config['port'],
        'settings': {
            'clients': [
                {
                    'id': config['id']
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
            'startCommand': ['xray', '-c', config['file']],
            'fileContent': Xray.xrayConfig(inboundConfig),
            'filePath': config['file'],
            'envVar': {}
        },
        'aider': None
    }

def vlessTest(vlessConfig: dict) -> list:
    result = []
    for key, value in vlessConfig.items(): # vlessConfig -> config
        config[key] = value

    # TCP stream
    streamInfo = Xray.loadTcpStream(False, '', '')
    result.append(loadVlessStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVlessStream(streamInfo, None))
    for flow in Xray.xtlsFlowList:
        streamInfo = Xray.loadTcpStream(False, '', '')
        xtlsFlow, streamInfo = Xray.addXtlsConfig(streamInfo, config['cert'], config['key'], config['host'], flow)
        result.append(loadVlessStream(streamInfo, xtlsFlow))

    streamInfo = Xray.loadTcpStream(True, config['host'], '/')
    result.append(loadVlessStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVlessStream(streamInfo, None))

    # mKCP stream
    for obfs in Xray.udpObfsList:
        streamInfo = Xray.loadKcpStream(config['passwd'], obfs)
        result.append(loadVlessStream(streamInfo, None))
        streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
        result.append(loadVlessStream(streamInfo, None))
        for flow in Xray.xtlsFlowList:
            streamInfo = Xray.loadKcpStream(config['passwd'], obfs)
            xtlsFlow, streamInfo = Xray.addXtlsConfig(streamInfo, config['cert'], config['key'], config['host'], flow)
            result.append(loadVlessStream(streamInfo, xtlsFlow))

    # WebSocket stream
    streamInfo = Xray.loadWsStream(config['host'], config['path'], False)
    result.append(loadVlessStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVlessStream(streamInfo, None))

    streamInfo = Xray.loadWsStream(config['host'], config['path'], True)
    result.append(loadVlessStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVlessStream(streamInfo, None))

    # HTTP/2 stream
    streamInfo = Xray.loadH2Stream(config['host'], config['path'])
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVlessStream(streamInfo, None))

    # QUIC stream
    for method in Xray.quicMethodList:
        for obfs in Xray.udpObfsList:
            streamInfo = Xray.loadQuicStream(method, config['passwd'], obfs)
            streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
            result.append(loadVlessStream(streamInfo, None))

    # GRPC stream
    streamInfo = Xray.loadGrpcStream(config['service'])
    result.append(loadVlessStream(streamInfo, None))
    streamInfo = Xray.addTlsConfig(streamInfo, config['cert'], config['key'], config['host'])
    result.append(loadVlessStream(streamInfo, None))

    return result
