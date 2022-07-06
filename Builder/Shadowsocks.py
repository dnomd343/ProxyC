#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from Basis.Methods import ssMethods


def loadConfig(proxyInfo: dict, socksInfo: dict) -> dict:  # load basic config option
    config = {
        'server': proxyInfo['server'],
        'server_port': proxyInfo['port'],  # type -> int
        'local_address': socksInfo['addr'],
        'local_port': socksInfo['port'],  # type -> int
        'method': proxyInfo['method'],
        'password': proxyInfo['passwd'],
    }
    if proxyInfo['plugin'] is not None:  # with plugin
        config['plugin'] = proxyInfo['plugin']['type']
        config['plugin_opts'] = proxyInfo['plugin']['param']
    return config


def pluginUdp(plugin: str, pluginParam: str) -> bool:  # whether the plugin uses UDP
    if plugin in ['obfs-local', 'simple-tls', 'ck-client', 'gq-client', 'mtt-client', 'rabbit-plugin']:
        return False  # UDP is not used
    if plugin in ['v2ray-plugin', 'xray-plugin', 'gost-plugin']:
        if 'mode=quic' not in pluginParam.split(';'):  # non-quic mode does not use UDP
            return False
    return True  # UDP is assumed by default


def ssRust(proxyInfo: dict, socksInfo: dict, isUdp: bool, isLegacy: bool = False) -> tuple[dict, list]:
    config = loadConfig(proxyInfo, socksInfo)
    if isUdp:  # Proxy UDP traffic
        config['mode'] = 'tcp_and_udp'
    return config, ['ss-rust-local', '-v']


def ssLibev(proxyInfo: dict, socksInfo: dict, isUdp: bool, isLegacy: bool = False) -> tuple[dict, list]:
    config = loadConfig(proxyInfo, socksInfo)
    if isUdp:  # Proxy UDP traffic
        config['mode'] = 'tcp_and_udp'
    return config, ['ss-libev-legacy-local' if isLegacy else 'ss-libev-local', '-v']


def ssPython(proxyInfo: dict, socksInfo: dict, isUdp: bool, isLegacy: bool = False) -> tuple[dict, list]:
    config = loadConfig(proxyInfo, socksInfo)
    mbedtlsMethods = [
        'aes-128-cfb128',
        'aes-192-cfb128',
        'aes-256-cfb128',
        'camellia-128-cfb128',
        'camellia-192-cfb128',
        'camellia-256-cfb128',
    ]
    if not isLegacy:  # only for latest version
        if config['method'] in mbedtlsMethods:  # mbedtls methods should use prefix `mbedtls:`
            config['method'] = 'mbedtls:' + config['method']
        if config['method'] in ['idea-cfb', 'seed-cfb']:  # Only older versions of openssl are supported
            config['extra_opts'] = '--libopenssl=libcrypto.so.1.0.0'
    if not isUdp:
        config['no_udp'] = True  # UDP traffic is not proxied
    config['shadowsocks'] = 'ss-python-legacy-local' if isLegacy else 'ss-python-local'
    return config, ['ss-bootstrap-local', '--debug', '-vv']


def load(proxyInfo: dict, socksInfo: dict, configFile: str) -> tuple[list, str, None]:
    if proxyInfo['plugin'] is None:  # UDP is enabled when server without plugin
        isUdp = True
    else:
        isUdp = not pluginUdp(  # check the UDP conflict status of plugins
            proxyInfo['plugin']['type'], proxyInfo['plugin']['param']
        )
    if proxyInfo['method'] not in ssMethods['all']:  # unknown shadowsocks method
        raise RuntimeError('Unknown shadowsocks method')
    for client in ssMethods:  # traverse all shadowsocks client
        if proxyInfo['method'] not in ssMethods[client] or client != 'all':
            continue
        ssLoadConfig = None
        if 'rust' in client: ssLoadConfig = ssRust
        if 'libev' in client: ssLoadConfig = ssLibev
        if 'python' in client: ssLoadConfig = ssPython
        ssConfig, ssClient = ssLoadConfig(proxyInfo, socksInfo, isUdp, 'legacy' in client)  # generate config file
        return ssClient + ['-c', configFile], json.dumps(ssConfig), None  # tuple[command, fileContent, envVar]
