#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ssMethods = { # methods support of different Shadowsocks project
    'ss-rust': [  # table method removed refer to https://github.com/shadowsocks/shadowsocks-rust/issues/887
        'none', 'plain', 'rc4', 'rc4-md5',
        'aes-128-ccm', 'aes-256-ccm',
        'aes-128-gcm', 'aes-256-gcm',
        'aes-128-gcm-siv', 'aes-256-gcm-siv',
        'aes-128-ctr', 'aes-192-ctr', 'aes-256-ctr',
        'aes-128-ofb', 'aes-192-ofb', 'aes-256-ofb',
        'aes-128-cfb', 'aes-192-cfb', 'aes-256-cfb',
        'aes-128-cfb1', 'aes-192-cfb1', 'aes-256-cfb1',
        'aes-128-cfb8', 'aes-192-cfb8', 'aes-256-cfb8',
        'aes-128-cfb128', 'aes-192-cfb128', 'aes-256-cfb128',
        'camellia-128-ctr', 'camellia-192-ctr', 'camellia-256-ctr',
        'camellia-128-ofb', 'camellia-192-ofb', 'camellia-256-ofb',
        'camellia-128-cfb', 'camellia-192-cfb', 'camellia-256-cfb',
        'camellia-128-cfb1', 'camellia-192-cfb1', 'camellia-256-cfb1',
        'camellia-128-cfb8', 'camellia-192-cfb8', 'camellia-256-cfb8',
        'camellia-128-cfb128', 'camellia-192-cfb128', 'camellia-256-cfb128',
        'chacha20-ietf', 'chacha20-ietf-poly1305', 'xchacha20-ietf-poly1305',
        '2022-blake3-aes-128-gcm', '2022-blake3-aes-256-gcm',
        '2022-blake3-chacha8-poly1305', '2022-blake3-chacha20-poly1305',
    ],
    'ss-libev': [
        'rc4', 'rc4-md5', 'bf-cfb',
        'aes-128-gcm', 'aes-192-gcm', 'aes-256-gcm',
        'aes-128-ctr', 'aes-192-ctr', 'aes-256-ctr',
        'aes-128-cfb', 'aes-192-cfb', 'aes-256-cfb',
        'camellia-128-cfb', 'camellia-192-cfb', 'camellia-256-cfb',
        'salsa20', 'chacha20', 'chacha20-ietf',
        'chacha20-ietf-poly1305', 'xchacha20-ietf-poly1305',
    ],
    'ss-python': [
        'table', 'rc4', 'rc4-md5',
        'aes-128-gcm', 'aes-192-gcm', 'aes-256-gcm',
        'aes-128-ctr', 'aes-192-ctr', 'aes-256-ctr',
        'aes-128-ocb', 'aes-192-ocb', 'aes-256-ocb',
        'aes-128-ofb', 'aes-192-ofb', 'aes-256-ofb',
        'aes-128-cfb', 'aes-192-cfb', 'aes-256-cfb',
        'aes-128-cfb1', 'aes-192-cfb1', 'aes-256-cfb1',
        'aes-128-cfb8', 'aes-192-cfb8', 'aes-256-cfb8',
        'aes-128-cfb128', 'aes-192-cfb128', 'aes-256-cfb128',
        'camellia-128-cfb', 'camellia-192-cfb', 'camellia-256-cfb',
        'camellia-128-cfb128', 'camellia-192-cfb128', 'camellia-256-cfb128',
        'rc2-cfb', 'bf-cfb', 'cast5-cfb', 'des-cfb', 'idea-cfb', 'seed-cfb',
        'salsa20', 'chacha20', 'xchacha20', 'chacha20-ietf', 'chacha20-poly1305',
        'chacha20-ietf-poly1305', 'xchacha20-ietf-poly1305',
    ],
    'ss-python-legacy': [
        'table', 'rc4', 'rc4-md5',
        'aes-128-ctr', 'aes-192-ctr', 'aes-256-ctr',
        'aes-128-ofb', 'aes-192-ofb', 'aes-256-ofb',
        'aes-128-cfb', 'aes-192-cfb', 'aes-256-cfb',
        'aes-128-cfb1', 'aes-192-cfb1', 'aes-256-cfb1',
        'aes-128-cfb8', 'aes-192-cfb8', 'aes-256-cfb8',
        'camellia-128-cfb', 'camellia-192-cfb', 'camellia-256-cfb',
        'rc2-cfb', 'bf-cfb', 'cast5-cfb', 'des-cfb', 'idea-cfb', 'seed-cfb',
        'salsa20', 'salsa20-ctr', 'chacha20',
    ]
}

ssAllMethods = set()
[ssAllMethods.update(ssMethods[x]) for x in ssMethods]
ssAllMethods = sorted(list(ssAllMethods))  # methods of Shadowsocks

ssrMethods = [  # methods of ShadowsocksR
    'aes-128-ctr', 'aes-192-ctr', 'aes-256-ctr',
    'aes-128-gcm', 'aes-192-gcm', 'aes-256-gcm',
    'aes-128-ofb', 'aes-192-ofb', 'aes-256-ofb',
    'aes-128-cfb', 'aes-192-cfb', 'aes-256-cfb',
    'aes-128-cfb1', 'aes-192-cfb1', 'aes-256-cfb1',
    'aes-128-cfb8', 'aes-192-cfb8', 'aes-256-cfb8',
    'camellia-128-cfb', 'camellia-192-cfb', 'camellia-256-cfb',
    'none', 'table', 'rc4', 'rc4-md5', 'rc2-cfb', 'rc4-md5-6',
    'bf-cfb', 'cast5-cfb', 'des-cfb', 'idea-cfb', 'seed-cfb',
    'salsa20', 'xsalsa20', 'chacha20', 'xchacha20', 'chacha20-ietf',
]

ssrProtocols = [  # protocols of ShadowsocksR
    'origin', 'auth_simple',
    'verify_sha1', 'verify_simple', 'verify_deflate',
    'auth_sha1', 'auth_sha1_v2', 'auth_sha1_v4',
    'auth_aes128', 'auth_aes128_md5', 'auth_aes128_sha1',
    'auth_chain_a', 'auth_chain_b', 'auth_chain_c',
    'auth_chain_d', 'auth_chain_e', 'auth_chain_f',
]

ssrObfuscations = [ # obfuscations of ShadowsocksR (obfs)
    'plain', 'http_post', 'http_simple', 'random_head',
    'tls_simple', 'tls1.2_ticket_auth', 'tls1.2_ticket_fastauth',
]
