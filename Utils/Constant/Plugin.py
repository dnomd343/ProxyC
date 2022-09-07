#!/usr/bin/env python3
# -*- coding: utf-8 -*-

Plugins = {
    'simple-obfs': ['obfs-local', 'obfs-server'],
    'simple-tls': ['simple-tls'],
    'v2ray': ['v2ray-plugin'],
    'xray': ['xray-plugin'],
    'kcptun': ['kcptun-client', 'kcptun-server'],
    'gost': ['gost-plugin'],
    'cloak': ['ck-client', 'ck-server'],
    'go-quiet': ['gq-client', 'gq-server'],
    'mos-tls-tunnel': ['mtt-client', 'mtt-server'],
    'rabbit': ['rabbit-plugin', 'rabbit'],
    'qtun': ['qtun-client', 'qtun-server'],
    'gun': ['gun-plugin'],
}

pluginClients = [p[0] for _, p in Plugins.items()]  # plugin client list -> obfs-local / simple-tls / ...

Plugins = {caption: {  # format plugins info
    'client': plugin[0],
    'server': plugin[1 if len(plugin) > 1 else 0]
} for caption, plugin in Plugins.items()}
