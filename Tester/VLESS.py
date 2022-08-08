#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from Tester import Xray
from Builder import VLESS
from Basis.Test import Settings
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Constant import xtlsFlows
from Basis.Functions import md5Sum, genUUID, getAvailablePort


def loadServer(configFile: str, proxyInfo: dict, streamConfig: dict, xtlsFlow: str or None) -> Process:
    vlessConfig = Xray.loadConfig({
        'protocol': 'vless',
        'listen': proxyInfo['server'],
        'port': proxyInfo['port'],
        'settings': {
            'clients': [{
                'id': proxyInfo['id'],
                **({} if xtlsFlow is None else {
                    'flow': xtlsFlow
                })
            }],
            'decryption': 'none'
        },
        'streamSettings': streamConfig
    })
    serverFile = os.path.join(Settings['workDir'], configFile)
    return Process(Settings['workDir'], cmd = ['xray', '-c', serverFile], file = {
        'path': serverFile,
        'content': json.dumps(vlessConfig)
    }, isStart = False)


def loadClient(configFile: str, proxyInfo: dict, socksInfo: dict) -> Process:  # load client process
    clientFile = os.path.join(Settings['workDir'], configFile)
    vlessCommand, vlessConfig, _ = VLESS.load(proxyInfo, socksInfo, clientFile)
    return Process(Settings['workDir'], cmd = vlessCommand, file = {
        'path': clientFile,
        'content': vlessConfig
    }, isStart = False)


def loadTest(stream: dict) -> dict:
    proxyInfo = {  # connection info
        'server': Settings['serverBind'],
        'port': getAvailablePort(),
        'method': 'none',
        'id': genUUID(),  # random uuid v5
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
    configName = 'vless_%s' % (md5Sum(stream['caption'])[:8])
    testInfo = {  # release test info
        'caption': 'VLESS test: %s' % stream['caption'],
        'client': loadClient(configName + '_client.json', proxyInfo, socksInfo),
        'server': loadServer(configName + '_server.json', proxyInfo, stream['server'], xtlsFlow),
        'socks': socksInfo,  # exposed socks5 address
        'interface': {
            'addr': proxyInfo['server'],
            'port': proxyInfo['port'],
        }
    }
    logging.debug('New VLESS test -> %s' % testInfo)
    return testInfo


def load():
    streams = Xray.loadStream()  # load xray-core stream list
    for stream in streams:  # test all stream cases
        yield loadTest(stream)
    logging.info('VLESS test yield complete')
