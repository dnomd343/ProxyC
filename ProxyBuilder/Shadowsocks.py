#!/usr/bin/python
# -*- coding:utf-8 -*-

import json

ssMethodList = { # Shadowsocks各版本加密方式支持
    'ss-python': [
        'aes-128-gcm',
        'aes-192-gcm',
        'aes-256-gcm',
        'aes-128-ctr',
        'aes-192-ctr',
        'aes-256-ctr',
        'aes-128-ocb',
        'aes-192-ocb',
        'aes-256-ocb',
        'aes-128-ofb',
        'aes-192-ofb',
        'aes-256-ofb',
        'aes-128-cfb',
        'aes-192-cfb',
        'aes-256-cfb',
        'aes-128-cfb1',
        'aes-192-cfb1',
        'aes-256-cfb1',
        'aes-128-cfb8',
        'aes-192-cfb8',
        'aes-256-cfb8',
        'aes-128-cfb128',
        'aes-192-cfb128',
        'aes-256-cfb128',
        'camellia-128-cfb',
        'camellia-192-cfb',
        'camellia-256-cfb',
        'camellia-128-cfb128',
        'camellia-192-cfb128',
        'camellia-256-cfb128',
        'table',
        'rc4',
        'rc4-md5',
        'rc2-cfb',
        'bf-cfb',
        'cast5-cfb',
        'des-cfb',
        'idea-cfb',
        'seed-cfb',
        'salsa20',
        'xchacha20',
        'chacha20',
        'chacha20-ietf',
        'chacha20-poly1305',
        'chacha20-ietf-poly1305',
        'xchacha20-ietf-poly1305',
    ],
    'ss-python-legacy': [
        'aes-128-ctr',
        'aes-192-ctr',
        'aes-256-ctr',
        'aes-128-ofb',
        'aes-192-ofb',
        'aes-256-ofb',
        'aes-128-cfb',
        'aes-192-cfb',
        'aes-256-cfb',
        'aes-128-cfb1',
        'aes-192-cfb1',
        'aes-256-cfb1',
        'aes-128-cfb8',
        'aes-192-cfb8',
        'aes-256-cfb8',
        'camellia-128-cfb',
        'camellia-192-cfb',
        'camellia-256-cfb',
        'table',
        'rc4',
        'rc4-md5',
        'rc2-cfb',
        'bf-cfb',
        'cast5-cfb',
        'des-cfb',
        'idea-cfb',
        'seed-cfb',
        'salsa20',
        'salsa20-ctr',
        'chacha20',
    ],
    'ss-libev': [
        'aes-128-gcm',
        'aes-192-gcm',
        'aes-256-gcm',
        'aes-128-ctr',
        'aes-192-ctr',
        'aes-256-ctr',
        'aes-128-cfb',
        'aes-192-cfb',
        'aes-256-cfb',
        'camellia-128-cfb',
        'camellia-192-cfb',
        'camellia-256-cfb',
        'rc4',
        'rc4-md5',
        'bf-cfb',
        'salsa20',
        'chacha20',
        'chacha20-ietf',
        'chacha20-ietf-poly1305',
        'xchacha20-ietf-poly1305',
    ],
    'ss-libev-legacy': [
        'aes-128-ctr',
        'aes-192-ctr',
        'aes-256-ctr',
        'aes-128-cfb',
        'aes-192-cfb',
        'aes-256-cfb',
        'camellia-128-cfb',
        'camellia-192-cfb',
        'camellia-256-cfb',
        'table',
        'rc4',
        'rc4-md5',
        'rc2-cfb',
        'bf-cfb',
        'cast5-cfb',
        'des-cfb',
        'idea-cfb',
        'seed-cfb',
        'salsa20',
        'chacha20',
        'chacha20-ietf',
    ],
    'ss-rust': [
        'aes-128-gcm',
        'aes-256-gcm',
        'plain',
        'none',
        'chacha20-ietf-poly1305',
    ]
}

def __baseConfig(proxyInfo: dict, socksPort: int) -> dict: # 生成基本配置
    config = {
        'server': proxyInfo['server'],
        'server_port': proxyInfo['port'],
        'local_address': '127.0.0.1',
        'local_port': socksPort,
        'method': proxyInfo['method'],
        'password': proxyInfo['passwd'],
    }
    if proxyInfo['plugin'] is not None: # 带插件
        config['plugin'] = proxyInfo['plugin']['type']
        config['plugin_opts'] = proxyInfo['plugin']['param']
    return config

def __pluginWithUdp(plugin: str, pluginParam: str) -> bool: # 插件是否使用UDP通讯
    if plugin in ['obfs-local', 'simple-tls', 'ck-client', 'gq-client',
                  'mtt-client', 'rabbit-plugin', 'gun-plugin']: # 不使用UDP通讯的插件
        return False
    if plugin in ['v2ray-plugin', 'xray-plugin', 'gost-plugin']:
        if 'mode=quic' not in pluginParam.split(';'): # 非quic模式不使用UDP通讯
            return False
    return True # 默认假定占用UDP

def __ssPython(proxyInfo: dict, socksPort: int,
               isUdp: bool, isLegacy: bool = False) -> tuple[dict, str]: # ss-python配置生成
    config = __baseConfig(proxyInfo, socksPort)
    mbedtlsMethods = [
        'aes-128-cfb128',
        'aes-192-cfb128',
        'aes-256-cfb128',
        'camellia-128-cfb128',
        'camellia-192-cfb128',
        'camellia-256-cfb128',
    ]
    if not isLegacy: # 新版本特性
        if config['method'] in mbedtlsMethods: # mbedtls库流加密
            config['method'] = 'mbedtls:' + config['method']
        if config['method'] in ['idea-cfb', 'seed-cfb']: # 仅openssl旧版本支持
            config['extra_opts'] = '--libopenssl=libcrypto.so.1.0.0'
    if not isUdp:
        config['no_udp'] = True # 关闭UDP代理
    config['shadowsocks'] = 'ss-python-legacy-local' if isLegacy else 'ss-python-local'
    return config, 'ss-bootstrap-local'

def __ssLibev(proxyInfo: dict, socksPort: int,
              isUdp: bool, isLegacy: bool = False) -> tuple[dict, str]: # ss-libev配置生成
    config = __baseConfig(proxyInfo, socksPort)
    if isUdp:
        config['mode'] = 'tcp_and_udp'
    return config, 'ss-libev-legacy-local' if isLegacy else 'ss-libev-local'
    
def __ssRust(proxyInfo: dict, socksPort: int, isUdp: bool) -> tuple[dict, str]: # ss-rust配置生成
    config = __baseConfig(proxyInfo, socksPort)
    if isUdp:
        config['mode'] = 'tcp_and_udp'
    return config, 'ss-rust-local'

def load(proxyInfo: dict, socksPort: int, configFile: str) -> tuple[list or None, str or None, dict or None]:
    """
    Shadowsocks配置载入
        proxyInfo: 节点信息
        socksPort: 本地通讯端口
        configFile: 配置文件路径

            return startCommand, fileContent, envVar
    """
    if proxyInfo['plugin'] is None: # 无插件时启用UDP
        isUdp = True
    else:
        isUdp = not __pluginWithUdp( # 获取插件UDP冲突状态
            proxyInfo['plugin']['type'], proxyInfo['plugin']['param']
        )
    if proxyInfo['method'] in ssMethodList['ss-libev']: # 按序匹配客户端
        config, ssFile = __ssLibev(proxyInfo, socksPort, isUdp)
    elif proxyInfo['method'] in ssMethodList['ss-libev-legacy']:
        config, ssFile = __ssLibev(proxyInfo, socksPort, isUdp, isLegacy = True)
    elif proxyInfo['method'] in ssMethodList['ss-python']:
        config, ssFile = __ssPython(proxyInfo, socksPort, isUdp)
    elif proxyInfo['method'] in ssMethodList['ss-python-legacy']:
        config, ssFile = __ssPython(proxyInfo, socksPort, isUdp, isLegacy = True)
    elif proxyInfo['method'] in ssMethodList['ss-rust']:
        config, ssFile = __ssRust(proxyInfo, socksPort, isUdp)
    else:
        raise Exception('Unknown Shadowsocks method') # 无匹配加密方式
    return [ssFile, '-c', configFile], json.dumps(config), {}
