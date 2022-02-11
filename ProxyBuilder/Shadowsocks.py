#!/usr/bin/python
# -*- coding:utf-8 -*-

import json

ssMethodList = { # shadowsocks各版本支持的加密方式
    "ss-python": [
        "aes-128-gcm",
        "aes-192-gcm",
        "aes-256-gcm",
        "aes-128-ctr",
        "aes-192-ctr",
        "aes-256-ctr",
        "aes-128-ocb",
        "aes-192-ocb",
        "aes-256-ocb",
        "aes-128-ofb",
        "aes-192-ofb",
        "aes-256-ofb",
        "aes-128-cfb",
        "aes-192-cfb",
        "aes-256-cfb",
        "aes-128-cfb1",
        "aes-192-cfb1",
        "aes-256-cfb1",
        "aes-128-cfb8",
        "aes-192-cfb8",
        "aes-256-cfb8",
        "aes-128-cfb128",
        "aes-192-cfb128",
        "aes-256-cfb128",
        "camellia-128-cfb",
        "camellia-192-cfb",
        "camellia-256-cfb",
        "camellia-128-cfb128",
        "camellia-192-cfb128",
        "camellia-256-cfb128",
        "table",
        "rc4",
        "rc4-md5",
        "rc2-cfb",
        "bf-cfb",
        "cast5-cfb",
        "des-cfb",
        "idea-cfb",
        "seed-cfb",
        "salsa20",
        "xchacha20",
        "chacha20",
        "chacha20-ietf",
        "chacha20-poly1305",
        "chacha20-ietf-poly1305",
        "xchacha20-ietf-poly1305",
    ],
    "ss-python-legacy": [
        "aes-128-ctr",
        "aes-192-ctr",
        "aes-256-ctr",
        "aes-128-ofb",
        "aes-192-ofb",
        "aes-256-ofb",
        "aes-128-cfb",
        "aes-192-cfb",
        "aes-256-cfb",
        "aes-128-cfb1",
        "aes-192-cfb1",
        "aes-256-cfb1",
        "aes-128-cfb8",
        "aes-192-cfb8",
        "aes-256-cfb8",
        "camellia-128-cfb",
        "camellia-192-cfb",
        "camellia-256-cfb",
        "table",
        "rc4",
        "rc4-md5",
        "rc2-cfb",
        "bf-cfb",
        "cast5-cfb",
        "des-cfb",
        "idea-cfb",
        "seed-cfb",
        "salsa20",
        "salsa20-ctr",
        "chacha20",
    ],
    "ss-libev": [
        "aes-128-gcm",
        "aes-192-gcm",
        "aes-256-gcm",
        "aes-128-ctr",
        "aes-192-ctr",
        "aes-256-ctr",
        "aes-128-cfb",
        "aes-192-cfb",
        "aes-256-cfb",
        "camellia-128-cfb",
        "camellia-192-cfb",
        "camellia-256-cfb",
        "rc4",
        "rc4-md5",
        "bf-cfb",
        "salsa20",
        "chacha20",
        "chacha20-ietf",
        "chacha20-ietf-poly1305",
        "xchacha20-ietf-poly1305",
    ],
    "ss-libev-legacy": [
        "aes-128-ctr",
        "aes-192-ctr",
        "aes-256-ctr",
        "aes-128-cfb",
        "aes-192-cfb",
        "aes-256-cfb",
        "camellia-128-cfb",
        "camellia-192-cfb",
        "camellia-256-cfb",
        "table",
        "rc4",
        "rc4-md5",
        "rc2-cfb",
        "bf-cfb",
        "cast5-cfb",
        "des-cfb",
        "idea-cfb",
        "seed-cfb",
        "salsa20",
        "chacha20",
        "chacha20-ietf",
    ],
    "ss-rust": [
        "aes-128-gcm",
        "aes-256-gcm",
        "plain",
        "none",
        "chacha20-ietf-poly1305",
    ]
}

def __baseJSON(proxyInfo, socksPort): # 生成JSON基本结构
    jsonContent = {
        'server': proxyInfo['server'],
        'server_port': int(proxyInfo['port']),
        'local_address': '127.0.0.1',
        'local_port': int(socksPort),
        'password': proxyInfo['password'],
        'method': proxyInfo['method'],
    }
    if proxyInfo['plugin'] != '':
        jsonContent['plugin'] = proxyInfo['plugin']
        jsonContent['plugin_opts'] = proxyInfo['pluginParam']
    return jsonContent

def __pluginUdpCheck(plugin, pluginParam): # 插件是否使用UDP通讯
    if plugin == '': # 无插件
        return False
    noUdpPlugin = [ # 不使用UDP通讯的插件
        'obfs-local',
        'simple-tls',
        'ck-client',
        'gq-client',
        'mtt-client',
        'rabbit-plugin',
        'gun-plugin',
    ]
    onlyUdpPlugin = [ # 仅使用UDP通讯的插件
        'kcptun-client',
        'qtun-client',
    ]
    if plugin in noUdpPlugin:
        return False
    if plugin in onlyUdpPlugin:
        return True
    if plugin == 'v2ray-plugin' or plugin == 'xray-plugin' or plugin == 'gost-plugin':
        if not 'mode=quic' in pluginParam.split(';'):
            return False
    return True # 默认假定占用UDP

def __ssPython(proxyInfo, socksPort, isLegacy = False): # ss-python配置文件生成
    jsonContent = __baseJSON(proxyInfo, socksPort)
    specialMethods = [
        'aes-128-cfb128',
        'aes-192-cfb128',
        'aes-256-cfb128',
        'camellia-128-cfb128',
        'camellia-192-cfb128',
        'camellia-256-cfb128',
    ]
    if isLegacy == False: # 仅新版本支持
        if jsonContent['method'] in specialMethods:
            jsonContent['method'] = 'mbedtls:' + jsonContent['method']
        if jsonContent['method'] == 'idea-cfb' or jsonContent['method'] == 'seed-cfb':
            jsonContent['extra_opts'] = '--libopenssl=libcrypto.so.1.0.0'
    if proxyInfo['udp'] != True:
        jsonContent['no_udp'] = True
    if isLegacy == True:
        jsonContent['shadowsocks'] = 'ss-python-legacy-local'
    else:
        jsonContent['shadowsocks'] = 'ss-python-local'
    return jsonContent, 'ss-bootstrap-local'

def __ssLibev(proxyInfo, socksPort, isLegacy = False): # ss-libev配置文件生成
    jsonContent = __baseJSON(proxyInfo, socksPort)
    if proxyInfo['udp'] == True:
        jsonContent['mode'] = 'tcp_and_udp'
    if isLegacy == True:
        return jsonContent, 'ss-libev-legacy-local'
    else:
        return jsonContent, 'ss-libev-local'
    
def __ssRust(proxyInfo, socksPort): # ss-rust配置文件生成
    jsonContent = __baseJSON(proxyInfo, socksPort)
    if proxyInfo['udp'] == True:
        jsonContent['mode'] = 'tcp_and_udp'
    return jsonContent, 'ss-rust-local'

def load(proxyInfo, socksPort, configFile): # Shadowsocks配置载入
    proxyInfo['udp'] = not __pluginUdpCheck(proxyInfo['plugin'], proxyInfo['pluginParam'])
    if proxyInfo['method'] in ssMethodList['ss-libev']:
        jsonContent, ssFile = __ssLibev(proxyInfo, socksPort)
    elif proxyInfo['method'] in ssMethodList['ss-libev-legacy']:
        jsonContent, ssFile = __ssLibev(proxyInfo, socksPort, isLegacy = True)
    elif proxyInfo['method'] in ssMethodList['ss-python']:
        jsonContent, ssFile = __ssPython(proxyInfo, socksPort)
    elif proxyInfo['method'] in ssMethodList['ss-python-legacy']:
        jsonContent, ssFile = __ssPython(proxyInfo, socksPort, isLegacy = True)
    elif proxyInfo['method'] in ssMethodList['ss-rust']:
        jsonContent, ssFile = __ssRust(proxyInfo, socksPort)
    else:
        return None, None # 匹配不到加密方式
    return [ ssFile, '-c', configFile ], json.dumps(jsonContent)
