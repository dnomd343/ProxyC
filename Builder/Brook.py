#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Basis.Functions import v6AddBracket

def loadOrigin(proxyInfo: dict) -> list:  # origin stream
    return ['client'] + [
        '--server', '%s:%i' % (v6AddBracket(proxyInfo['server']), proxyInfo['port']),
        '--password', proxyInfo['passwd'],
    ] + (['--udpovertcp'] if proxyInfo['stream']['uot'] else [])  # add uot option


def loadWebsocket(proxyInfo: dict) -> list:  # websocket stream
    isTls = proxyInfo['stream']['secure'] is not None  # ws or wss
    wsAddress = (('wss' if isTls else 'ws') + '://%s:%i%s') % (  # websocket address
        v6AddBracket(proxyInfo['stream']['host']), proxyInfo['port'], proxyInfo['stream']['path']
    )
    brookCommand = [
        'wssclient' if isTls else 'wsclient',
        '--address', '%s:%i' % (v6AddBracket(proxyInfo['server']), proxyInfo['port']),  # real address
        '--password', proxyInfo['passwd'],
    ] + (['--withoutBrookProtocol'] if proxyInfo['stream']['raw'] else [])  # raw transmission on ws or wss
    if not isTls:
        return brookCommand + ['--wsserver', wsAddress]
    return brookCommand + ['--wssserver', wsAddress] + (
        [] if proxyInfo['stream']['secure']['verify'] else ['--insecure']  # add tls options
    )


def load(proxyInfo: dict, socksInfo: dict, configFile: str) -> tuple[list, str, dict]:
    brookCommand = ['brook', '--debug', '--listen', ':'] + {  # debug module listen on random port
        'origin': loadOrigin,
        'ws': loadWebsocket,
    }[proxyInfo['stream']['type']](proxyInfo)  # choose origin or websocket stream
    brookCommand += ['--socks5', '%s:%i' % (v6AddBracket(socksInfo['addr']), socksInfo['port'])]
    return brookCommand, 'Config file %s no need' % configFile, {}  # command, fileContent, envVar
