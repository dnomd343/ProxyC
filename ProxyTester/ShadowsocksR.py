#!/usr/bin/python
# -*- coding:utf-8 -*-

config = {}

ssrMethodList = [
    "aes-128-cfb",
    "aes-192-cfb",
    "aes-256-cfb",
    "aes-128-cfb1",
    "aes-192-cfb1",
    "aes-256-cfb1",
    "aes-128-cfb8",
    "aes-192-cfb8",
    "aes-256-cfb8",
    "aes-128-ctr",
    "aes-192-ctr",
    "aes-256-ctr",
    "aes-128-gcm",
    "aes-192-gcm",
    "aes-256-gcm",
    "aes-128-ofb",
    "aes-192-ofb",
    "aes-256-ofb",
    "camellia-128-cfb",
    "camellia-192-cfb",
    "camellia-256-cfb",
    "none",
    "table",
    "rc4",
    "rc4-md5",
    "rc4-md5-6",
    "bf-cfb",
    "cast5-cfb",
    "des-cfb",
    "idea-cfb",
    "seed-cfb",
    "rc2-cfb",
    "salsa20",
    "xsalsa20",
    "chacha20",
    "xchacha20",
    "chacha20-ietf",
]

ssrProtocolList = [
    "origin",
    "verify_sha1",
    "verify_simple",
    "verify_deflate",
    "auth_simple",
    "auth_sha1",
    "auth_sha1_v2",
    "auth_sha1_v4",
    "auth_aes128",
    "auth_aes128_md5",
    "auth_aes128_sha1",
    "auth_chain_a",
    "auth_chain_b",
    "auth_chain_c",
    "auth_chain_d",
    "auth_chain_e",
    "auth_chain_f",
]

ssrObfsList = [
    "plain",
    "http_post",
    "http_simple",
    "tls_simple",
    "tls1.2_ticket_auth",
    "tls1.2_ticket_fastauth",
    "random_head",
]

def __ssrServerConfig(method: str, protocol: str, obfs: str, caption: str) -> list:
    proxyInfo = {
        'type': 'ssr',
        'server': '127.0.0.1',
        'port': config['port'],
        'passwd': config['passwd'],
        'method': method,
        'protocol': protocol,
        'obfs': obfs
    }
    serverCommand = [
        'ssr-server',
        '-p', str(config['port']),
        '-k', config['passwd'],
        '-m', method,
        '-O', protocol,
        '-o', obfs
    ]
    return [{
        'caption': caption,
        'proxy': proxyInfo,
        'server': {
            'startCommand': serverCommand,
            'fileContent': None,
            'filePath': None,
            'envVar': {}
        },
        'aider': None
    }]

def ssrTest(ssrConfig: dict) -> list:
    result = []
    for key, value in ssrConfig.items(): # ssrConfig -> config
        config[key] = value
    for method in ssrMethodList: # all ShadowsocksR methods
        result += __ssrServerConfig(method, 'origin', 'plain', 'ShadowsocksR method ' + method)
    for protocol in ssrProtocolList: # all ShadowsocksR protocol and obfs
        for obfs in ssrObfsList:
            result += __ssrServerConfig('table', protocol, obfs, 'ShadowsocksR protocol ' + protocol + ' obfs ' + obfs)
    return result
