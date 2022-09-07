#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# V2ray / Xray
vmessMethods = ['aes-128-gcm', 'chacha20-poly1305', 'auto', 'none', 'zero']

quicMethods = ['none', 'aes-128-gcm', 'chacha20-poly1305']
udpObfuscations = ['none', 'srtp', 'utp', 'wechat-video', 'dtls', 'wireguard']

xtlsFlows = ['xtls-origin', 'xtls-direct', 'xtls-splice']
xtlsFlows = {x: x.replace('-', '-rprx-') for x in xtlsFlows}

# Trojan-Go
trojanGoMethods = ['aes-128-gcm', 'aes-256-gcm', 'chacha20-ietf-poly1305']

# Hysteria
hysteriaProtocols = ['udp', 'wechat-video', 'faketcp']
