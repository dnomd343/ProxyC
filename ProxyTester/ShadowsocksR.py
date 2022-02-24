#!/usr/bin/python
# -*- coding:utf-8 -*-

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

def test(port, password):
    testList = []
    for method in ssrMethodList:
        proxyInfo = {
            'type': 'ssr',
            'server': '127.0.0.1',
            'port': int(port),
            'password': password,
            'method': method,
            'protocol': 'origin',
            'protocolParam': '',
            'obfs': 'plain',
            'obfsParam': ''
        }
        serverCommand = [
            'ssr-server',
            '-p', str(port),
            '-k', password,
            '-m', method,
            '-O', 'origin',
            '-o', 'plain'
        ]
        testList.append({
            'caption': 'ShadowsocksR method ' + method,
            'proxyInfo': proxyInfo,
            'serverCommand': serverCommand
        })
    for protocol in ssrProtocolList:
        for obfs in ssrObfsList:
            proxyInfo = {
                'type': 'ssr',
                'server': '127.0.0.1',
                'port': int(port),
                'password': password,
                'method': 'table',
                'protocol': protocol,
                'protocolParam': '',
                'obfs': obfs,
                'obfsParam': ''
            }
            serverCommand = [
                'ssr-server',
                '-p', str(port),
                '-k', password,
                '-m', 'table',
                '-O', protocol,
                '-o', obfs
            ]
            testList.append({
                'caption': 'ShadowsocksR protocol ' + protocol + ' obfs ' + obfs,
                'proxyInfo': proxyInfo,
                'serverCommand': serverCommand
            })
    return testList
