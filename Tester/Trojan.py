#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from Tester import Xray
from Builder import Trojan
from Utils.Logger import logger
from Utils.Tester import Settings
from Utils.Process import Process
from Utils.Constant import xtlsFlows
from Utils.Common import md5Sum, genFlag, getAvailablePort


def loadServer(configFile: str, proxyInfo: dict, streamConfig: dict, xtlsFlow: str or None) -> Process:
    trojanConfig = Xray.loadConfig({
        'protocol': 'trojan',
        'listen': proxyInfo['server'],
        'port': proxyInfo['port'],
        'settings': {
            'clients': [{
                'password': proxyInfo['passwd'],
                **({} if xtlsFlow is None else {
                    'flow': xtlsFlow
                })
            }],
        },
        'streamSettings': streamConfig
    })
    serverFile = os.path.join(Settings['workDir'], configFile)
    return Process(Settings['workDir'], cmd = ['xray', '-c', serverFile], file = {
        'path': serverFile,
        'content': json.dumps(trojanConfig)
    }, isStart = False)


def loadClient(configFile: str, proxyInfo: dict, socksInfo: dict) -> Process:  # load client process
    clientFile = os.path.join(Settings['workDir'], configFile)
    trojanCommand, trojanConfig, _ = Trojan.load(proxyInfo, socksInfo, clientFile)
    return Process(Settings['workDir'], cmd = trojanCommand, file = {
        'path': clientFile,
        'content': trojanConfig
    }, isStart = False)


def loadBasicTest(tcpTlsStream: dict) -> dict:
    proxyInfo = {  # connection info
        'server': Settings['serverBind'],
        'port': getAvailablePort(),
        'passwd': genFlag(length = 8),  # random password
        'stream': tcpTlsStream['info']
    }
    socksInfo = {  # socks5 interface for test
        'addr': Settings['clientBind'],
        'port': getAvailablePort()
    }
    trojanConfig = {
        'run_type': 'server',
        'local_addr': proxyInfo['server'],
        'local_port': proxyInfo['port'],
        'password': [proxyInfo['passwd']],
        'log_level': 0,  # 0 -> ALL / 1 -> INFO / 2 -> WARN / 3 -> ERROR / 4 -> FATAL / 5 -> OFF
        'ssl': {
            'cert': Settings['cert'],
            'key': Settings['key']
        }
    }
    serverFile = os.path.join(Settings['workDir'], 'trojan_basic_server.json')
    trojanServer = Process(Settings['workDir'], cmd = ['trojan', '-c', serverFile], file = {
        'path': serverFile,
        'content': json.dumps(trojanConfig)
    }, isStart = False)
    testInfo = {  # release test info
        'caption': 'Trojan test: basic connection',
        'client': loadClient('trojan_basic_client.json', proxyInfo, socksInfo),
        'server': trojanServer,
        'socks': socksInfo,  # exposed socks5 address
        'interface': {
            'addr': proxyInfo['server'],
            'port': proxyInfo['port'],
        }
    }
    logger.debug('New trojan test -> %s' % testInfo)
    return testInfo


def loadTest(stream: dict) -> dict:
    proxyInfo = {  # connection info
        'server': Settings['serverBind'],
        'port': getAvailablePort(),
        'passwd': genFlag(length = 8),  # random password
        'stream': stream['info']
    }
    socksInfo = {  # socks5 interface for test
        'addr': Settings['clientBind'],
        'port': getAvailablePort()
    }
    xtlsFlow = None
    if stream['info']['secure'] is not None and stream['info']['secure']['type'] == 'xtls':  # with XTLS secure
        xtlsFlow = xtlsFlows[stream['info']['secure']['flow']]
        xtlsFlow = xtlsFlow.replace('splice', 'direct')  # XTLS on server should use xtls-rprx-direct flow
    configName = 'trojan_%s' % (md5Sum(stream['caption'])[:8])
    testInfo = {  # release test info
        'caption': 'Trojan test: %s' % stream['caption'],
        'client': loadClient(configName + '_client.json', proxyInfo, socksInfo),
        'server': loadServer(configName + '_server.json', proxyInfo, stream['server'], xtlsFlow),
        'socks': socksInfo,  # exposed socks5 address
        'interface': {
            'addr': proxyInfo['server'],
            'port': proxyInfo['port'],
        }
    }
    logger.debug('New Trojan test -> %s' % testInfo)
    return testInfo


def load():
    streams = Xray.loadStream()  # load xray-core stream list
    yield loadBasicTest(streams[1])  # Trojan basic test -> TCP stream with TLS
    for stream in streams:  # test all stream cases
        yield loadTest(stream)
    logger.info('Trojan test yield complete')
