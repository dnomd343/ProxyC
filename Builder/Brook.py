#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Basis.Functions import hostFormat


def loadOrigin(proxyInfo: dict) -> list:  # origin stream
    return ['client'] + [
        '--server', '%s:%i' % (hostFormat(proxyInfo['server'], v6Bracket = True), proxyInfo['port']),
        '--password', proxyInfo['passwd'],
    ] + (['--udpovertcp'] if proxyInfo['stream']['uot'] else [])


def loadWebsocket(proxyInfo: dict) -> list:
    isTls = proxyInfo['stream']['secure'] is not None
    wsAddress = (('wss' if isTls else 'ws') + '://%s:%i%s') % (
        hostFormat(proxyInfo['stream']['host'], v6Bracket = True), proxyInfo['port'], proxyInfo['stream']['path']
    )
    brookCommand = [
        'wssclient' if isTls else 'wsclient',
        '--address', '%s:%i' % (hostFormat(proxyInfo['server'], v6Bracket = True), proxyInfo['port']),
        '--password', proxyInfo['passwd'],
    ] + (['--withoutBrookProtocol'] if proxyInfo['stream']['raw'] else [])
    if not isTls:
        return brookCommand + ['--wsserver', wsAddress]
    return brookCommand + ['--wssserver', wsAddress] + (
        [] if proxyInfo['stream']['secure']['verify'] else ['--insecure']
    )


def load(proxyInfo: dict, socksInfo: dict, configFile: str) -> tuple[list, str, dict]:
    brookCommand = ['brook', '--debug', '--listen', ':'] + {  # debug module listen on random port
        'origin': loadOrigin,
        'ws': loadWebsocket,
    }[proxyInfo['stream']['type']](proxyInfo) + [
        '--socks5', '%s:%i' % (hostFormat(socksInfo['addr'], v6Bracket = True), socksInfo['port'])
    ]
    return brookCommand, 'Config file %s no need' % configFile, {}
