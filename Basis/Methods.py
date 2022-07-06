#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ssMethods = { # methods support of different Shadowsocks project
    'ss-rust': [
        'none', 'plain',
        'table', 'rc4', 'rc4-md5',
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
ssAllMethods = list(ssAllMethods)
