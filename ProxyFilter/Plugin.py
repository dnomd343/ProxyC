#!/usr/bin/python
# -*- coding:utf-8 -*-

pluginList = [ # 插件列表
    'obfs-local',
    'simple-tls',
    'v2ray-plugin',
    'xray-plugin',
    'kcptun-client',
    'gost-plugin',
    'ck-client',
    'gq-client',
    'mtt-client',
    'rabbit-plugin',
    'qtun-client',
    'gun-plugin'
]

pluginAlias = { # 插件别名
    'obfs-local': [
        'obfs',
        'obfs-plugin',
        'obfs-client',
        'obfs-server',
        'simple-obfs',
    ],
    'simple-tls': [
        'tls-local',
        'tls-client',
        'tls-server',
        'tls-plugin',
        'simple-tls-local',
        'simple-tls-client',
        'simple-tls-server',
        'simple-tls-plugin',
    ],
    'v2ray-plugin': [
        'v2ray',
        'v2ray-local',
        'v2ray-client',
        'v2ray-server',
    ],
    'xray-plugin': [
        'xray',
        'xray-local',
        'xray-client',
        'xray-server',
    ],
    'kcptun-client': [
        'kcptun',
        'kcptun-local',
        'kcptun-server',
        'kcptun-plugin',
    ],
    'gost-plugin': [
        'gost',
        'gost-local',
        'gost-client',
        'gost-server',
    ],
    'ck-client': [
        'ck',
        'ck-local',
        'ck-server',
        'ck-plugin',
        'cloak',
        'cloak-local',
        'cloak-client',
        'cloak-server',
        'cloak-plugin',
    ],
    'gq-client': [
        'gq',
        'gq-local',
        'gq-server',
        'gq-plugin',
        'goquiet',
        'goquiet-local',
        'goquiet-client',
        'goquiet-server',
        'goquiet-plugin',
    ],
    'mtt-client': [
        'mtt',
        'mtt-local',
        'mtt-server',
        'mtt-plugin',
        'mos-tls-tunnel',
        'mos-tls-tunnel-local',
        'mos-tls-tunnel-client',
        'mos-tls-tunnel-server',
        'mos-tls-tunnel-plugin',
    ],
    'rabbit-plugin': [
        'rabbit',
        'rabbit-tcp',
        'rabbit-local',
        'rabbit-client',
        'rabbit-server',
    ],
    'qtun-client': [
        'qtun',
        'qtun-local',
        'qtun-server',
        'qtun-plugin',
    ],
    'gun-plugin': [
        'gun',
        'gun-local',
        'gun-client',
        'gun-server',
    ]
}

def pluginFormat(plugin): # 插件格式化
    plugin = plugin.replace('_', '-').lower().strip()
    if not plugin in pluginList: # 非标插件名
        for pluginName in pluginAlias:
            if plugin in pluginAlias[pluginName]: # 匹配别名列表
                return pluginName
    return plugin
