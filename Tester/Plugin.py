#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import json
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Constant import plugins
from Tester.Settings import Settings
from Basis.Functions import genFlag, hostFormat, getAvailablePort


pluginParams = {
    'SITE': Settings['site']
}

pluginConfig = {
    'simple-obfs': {
        'http mode': [
            'obfs=http',
            'obfs=http;obfs-host=${SITE}',
        ],
        'tls mode': [
            'obfs=tls',
            'obfs=tls;obfs-host=${SITE}',
        ],
        'http mode (with uri)': [
            'obfs=http',
            'obfs=http;obfs-host=${SITE};obfs-uri=${PATH}',
        ],
        'http mode (POST method)': [
            'obfs=http',
            'obfs=http;http-method=POST;obfs-host=${SITE}',
        ],
    },
    'simple-tls': {
        'http mode': [
            's;n=${HOST};cert=${CERT};key=${KEY}',
            'n=${HOST}',
        ],
        'websocket mode': [
            's;n=${HOST};cert=${CERT};key=${KEY};ws;ws-path=${PATH}',
            'n=${HOST};ws;ws-path=${PATH}',
        ],
        'http mode (with mux)': [
            's;cert=${CERT};key=${KEY};n=${HOST}',
            'n=${HOST};mux=8',
        ],
        'http mode (with auth key)': [
            's;n=${HOST};cert=${CERT};key=${KEY};auth=${PASSWD}',
            'n=${HOST};auth=${PASSWD}',
        ],
    },
    'v2ray': {
        'websocket mode': [
            'server',
            '',
        ],
        'websocket mode (with tls)': [
            'server;tls;host=${HOST};cert=${CERT};key=${KEY}',
            'tls;host=${HOST}',
        ],
        'websocket mode (with path)': [
            'server;path=${PATH}',
            'path=${PATH}',
        ],
        'quic mode': [
            'server;mode=quic;host=${HOST};cert=${CERT};key=${KEY}',
            'mode=quic;host=${HOST}',
        ],
    },
    'xray': {
        'websocket mode': [
            'server',
            '',
        ],
        'websocket mode (with tls)': [
            'server;tls;host=${HOST};cert=${CERT};key=${KEY}',
            'tls;host=${HOST}',
        ],
        'websocket mode (with path)': [
            'server;path=${PATH}',
            'path=${PATH}',
        ],
        'quic mode': [
            'server;mode=quic;host=${HOST};cert=${CERT};key=${KEY}',
            'mode=quic;host=${HOST}',
        ],
        'grpc mode': [
            'server;mode=grpc',
            'mode=grpc',
        ],
        'grpc mode (with tls)': [
            'server;tls;mode=grpc;host=${HOST};cert=${CERT};key=${KEY}',
            'tls;mode=grpc;host=${HOST}',
        ],
    },
    'kcptun': {
        'basic mode': [
            '', ''  # aka fast mode
        ],
        'with nocomp': [
            'nocomp', 'nocomp'
        ],
        'with key': [
            'key=${PASSWD}', 'key=${PASSWD}'
        ],
        'with multi conn': [
            'conn=8', 'conn=8'
        ],
    },
    'gost': {
        'ws mode': [
            'server;mode=ws',
            'mode=ws',
        ],
        'mws mode': [
            'server;mode=mws',
            'mode=mws;mux=1',
        ],
        'tls mode': [
            'server;cert=${CERT};key=${KEY};mode=tls',
            'serverName=${HOST};mode=tls',
        ],
        'mtls mode': [
            'server;cert=${CERT};key=${KEY};mode=mtls',
            'serverName=${HOST};mode=mtls;mux=1',
        ],
        'xtls mode': [
            'server;cert=${CERT};key=${KEY};mode=xtls',
            'serverName=${HOST};mode=xtls',
        ],
        'h2 mode': [
            'server;cert=${CERT};key=${KEY};mode=h2',
            'serverName=${HOST};mode=h2',
        ],
        'wss mode': [
            'server;cert=${CERT};key=${KEY};mode=wss',
            'serverName=${HOST};mode=wss',
        ],
        'mwss mode': [
            'server;cert=${CERT};key=${KEY};mode=mwss',
            'serverName=${HOST};mode=mwss;mux=1',
        ],
        'quic mode': [
            'server;cert=${CERT};key=${KEY};mode=quic',
            'serverName=${HOST};mode=quic',
        ],
        'grpc mode': [
            'server;cert=${CERT};key=${KEY};mode=grpc',
            'serverName=${HOST};mode=grpc',
        ],
    },
    'cloak': {},
    'go-quiet': {
        'chrome fingerprint': [
            os.path.join(Settings['workDir'], 'go-quiet_config_${RANDOM}.json'),
            'ServerName=${SITE};key=${PASSWD};TicketTimeHint=300;Browser=chrome',
        ],
        'firefox fingerprint': [
            os.path.join(Settings['workDir'], 'go-quiet_config_${RANDOM}.json'),
            'ServerName=${SITE};key=${PASSWD};TicketTimeHint=300;Browser=firefox',
        ],
    },
    'mos-tls-tunnel': {
        'basic mode': [
            'cert=${CERT};key=${KEY}',
            'n=${HOST}',
        ],
        'basic mode (with mux)': [
            'cert=${CERT};key=${KEY};mux',
            'n=${HOST};mux',
        ],
        'wss mode': [
            'wss;cert=${CERT};key=${KEY}',
            'wss;n=${HOST}',
        ],
        'wss mode (with path)': [
            'wss;cert=${CERT};key=${KEY};wss-path=${PATH}',
            'wss;n=${HOST};wss-path=${PATH}',
        ],
        'wss mode (with mux)': [
            'wss;cert=${CERT};key=${KEY};mux',
            'wss;n=${HOST};mux',
        ],
    },
    'rabbit': {
        'basic mode': [
            '${RABBIT_PORT}',
            'serviceAddr=127.0.0.1:${RABBIT_PORT};password=${PASSWD};tunnelN=6'  # emulate SIP003 (ipv4 localhost)
        ],
    },
    'qtun': {
        'basic mode': [
            'cert=${CERT};key=${KEY}',
            'host=${HOST}',
        ],
    },
    'gun': {
        'basic mode': [
            'server:cleartext',
            'client:cleartext',
        ],
        'basic mode (with tls)': [
            'server:${CERT}:${KEY}',
            'client:${HOST}',
        ],
    },
}


def kcptunLoad() -> None:
    for kcptunMode in ['fast', 'fast2', 'fast3', 'normal', 'manual']:  # traverse kcptun modes
        pluginConfig['kcptun'][kcptunMode + ' mode'] = ['mode=' + kcptunMode, 'mode=' + kcptunMode]
    for kcptunCrypt in ['aes', 'aes-128', 'aes-192', 'salsa20', 'blowfish',
                        'twofish', 'cast5', '3des', 'tea', 'xtea', 'xor', 'none']:  # traverse kcptun crypt
        pluginConfig['kcptun']['with %s crypt' % kcptunCrypt] = ['crypt=' + kcptunCrypt, 'crypt=' + kcptunCrypt]


def cloakLoad() -> None:
    ckKey = os.popen('ck-server -key').read()  # generate public and private key for cloak
    pluginParams['CK_PUBLIC'] = re.search(r'\s+(\S+)$', ckKey.split('\n')[0])[1]
    pluginParams['CK_PRIVATE'] = re.search(r'\s+(\S+)$', ckKey.split('\n')[1])[1]
    pluginParams['CK_UID'] = re.search(r'\s+(\S+)\n', os.popen('ck-server -uid').read())[1]  # generate uid for clock
    logging.info('generate cloak uid -> %s' % pluginParams['CK_UID'])
    logging.info('generate cloak key -> %s (Public) | %s (Private)' % (
        pluginParams['CK_PUBLIC'], pluginParams['CK_PRIVATE']
    ))
    ckPrefix = 'UID=${CK_UID};PublicKey=${CK_PUBLIC};ServerName=${SITE};'  # cloak plugin's basic command
    ckConfigPath = os.path.join(Settings['workDir'], 'cloak_config_${RANDOM}.json')  # clock server's config
    for ckMethod in ['plain', 'aes-128-gcm', 'aes-256-gcm', 'chacha20-poly1305']:  # traverse cloak encrypt methods
        pluginConfig['cloak']['%s method' % ckMethod] = [
            ckConfigPath, ckPrefix + 'EncryptionMethod=' + ckMethod
        ]
    for ckBrowser in ['chrome', 'firefox']:  # traverse cloak browser fingerprints
        pluginConfig['cloak']['%s fingerprint' % ckBrowser] = [
            ckConfigPath, ckPrefix + 'EncryptionMethod=plain;BrowserSig=' + ckBrowser
        ]
    pluginConfig['cloak']['single connection'] = [  # disable connection multiplexing
        ckConfigPath, ckPrefix + 'EncryptionMethod=plain;NumConn=0'
    ]


def rabbitShadowsocks(server: Process, pluginInfo: dict) -> Process:
    ssConfig = json.loads(server.file[0]['content'])  # modify origin config
    ssConfig.pop('plugin')  # remove plugin option
    ssConfig.pop('plugin_opts')
    rabbitBind = hostFormat(ssConfig['server'], v6Bracket=True)  # ipv4 / [ipv6]
    rabbitPort = ssConfig['server_port']
    ssConfig['server'] = '127.0.0.1'  # SIP003 use ipv4 localhost for communication
    ssConfig['server_port'] = int(pluginInfo['server']['param'])  # aka ${RABBIT_PORT}
    server.file[0]['content'] = json.dumps(ssConfig)
    server.setCmd(['sh', '-c', paramFill(
        'rabbit -mode s -password ${PASSWD} -rabbit-addr %s:%s' % (rabbitBind, rabbitPort)  # start rabbit-tcp
    ) + ' &\nexec ' + ' '.join(server.cmd)])  # shadowsocks as main process (rabbit as sub process)
    return server


def rabbitTrojanGo(server: Process, pluginInfo: dict) -> Process:
    trojanConfig = json.loads(server.file[0]['content'])  # modify origin config
    rabbitBind = hostFormat(trojanConfig['local_addr'], v6Bracket=True)  # ipv4 / [ipv6]
    rabbitPort = trojanConfig['local_port']
    trojanConfig['local_addr'] = '127.0.0.1'  # SIP003 use ipv4 localhost for communication
    trojanConfig['local_port'] = int(pluginInfo['server']['param'])  # aka ${RABBIT_PORT}
    trojanConfig['transport_plugin'] = {
        'enabled': True,
        'type': 'other',
        'command': 'rabbit',
        'arg': [
            '-mode', 's', '-password', paramFill('${PASSWD}'),
            '-rabbit-addr', '%s:%s' % (rabbitBind, rabbitPort)
        ]
    }
    server.file[0]['content'] = json.dumps(trojanConfig)
    return server


def inject(server: Process, pluginInfo: dict) -> Process:
    if pluginInfo['type'] == 'cloak':
        ckConfig = paramFill(json.dumps({
            'BypassUID': ['${CK_UID}'],
            'RedirAddr': '${SITE}',
            'PrivateKey': '${CK_PRIVATE}'
        }))
        server.setFile(server.file + [{  # add cloak config file
            'path': pluginInfo['server']['param'],
            'content': ckConfig
        }])
    elif pluginInfo['type'] == 'go-quiet':
        server.setFile(server.file + [{  # add gq-quiet config file
            'path': pluginInfo['server']['param'],
            'content': paramFill(json.dumps({'key': '${PASSWD}'}))
        }])
    return server


def ssInject(server: Process, pluginInfo: dict) -> Process:
    if pluginInfo['type'] == 'rabbit':  # hijack rabbit plugin config
        return rabbitShadowsocks(server, pluginInfo)
    return inject(server, pluginInfo)


def trojanInject(server: Process, pluginInfo: dict) -> Process:
    if pluginInfo['type'] == 'rabbit':  # hijack rabbit plugin config
        return rabbitTrojanGo(server, pluginInfo)
    return inject(server, pluginInfo)


def paramFill(param: str) -> str:
    for field in pluginParams:
        param = param.replace('${%s}' % field, pluginParams[field])  # fill ${XXX} field
    return param


def load(proxyType: str):
    if proxyType not in ['ss', 'trojan-go']:
        raise RuntimeError('Unknown proxy type for sip003 plugin')
    cloakLoad()  # init cloak config
    kcptunLoad()  # init kcptun config
    pluginParams.update({
        'HOST': Settings['host'],
        'CERT': Settings['cert'],
        'KEY': Settings['key'],
        'PASSWD': genFlag(length = 8),  # random password for test
        'PATH': '/' + genFlag(length = 6),  # random uri path for test
    })
    for pluginType in pluginConfig:
        for pluginTest, pluginTestInfo in pluginConfig[pluginType].items():  # traverse all plugin test item
            pluginParams['RANDOM'] = genFlag(length = 8)  # refresh RANDOM field
            pluginParams['RABBIT_PORT'] = str(getAvailablePort())  # allocate port before rabbit plugin start
            yield {
                'type': pluginType,
                'caption': pluginTest,
                'server': {  # plugin info for server
                    'type': plugins[pluginType]['server'],
                    'param': paramFill(pluginTestInfo[0]),
                },
                'client': {  # plugin info for client
                    'type': plugins[pluginType]['client'],
                    'param': paramFill(pluginTestInfo[1]),
                },
                'inject': ssInject if proxyType == 'ss' else trojanInject  # for some special plugins
            }
