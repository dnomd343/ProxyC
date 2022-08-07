#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Basis.Filter import rulesFilter
from Basis.Constant import pluginClients
from Basis.Functions import toStr, toStrTidy

pluginAlias = {
    'obfs-local': {'obfs', 'simple-obfs'},
    'simple-tls': {'tls', 'simple-tls'},
    'v2ray-plugin': {'v2ray'},
    'xray-plugin': {'xray'},
    'kcptun-client': {'kcptun'},
    'gost-plugin': {'gost'},
    'ck-client': {'ck', 'cloak'},
    'gq-client': {'gq', 'goquiet', 'go-quiet'},
    'mtt-client': {'mtt', 'mos-tls-tunnel'},
    'rabbit-plugin': {'rabbit', 'rabbit-tcp'},
    'qtun-client': {'qtun'},
    'gun-plugin': {'gun'},
}

pluginObject = rulesFilter({
    'type': {
        'type': str,
        'format': lambda s: pluginFormat(toStrTidy(s)),
        'filter': lambda s: s in pluginClients,
        'errMsg': 'Unknown SIP003 plugin'
    },
    'param': {
        'optional': True,
        'default': '',
        'type': str,
        'format': toStr,
        'errMsg': 'Invalid SIP003 param'
    }
})


def loadAlias() -> None:
    for plugin in pluginAlias:
        for alias in copy.copy(pluginAlias[plugin]):
            pluginAlias[plugin].update({  # better compatibility
                alias + '-local', alias + '-plugin',
                alias + '-client', alias + '-server',
            })


def pluginFormat(pluginName: str) -> str:
    pluginName = pluginName.replace('_', '-')
    for plugin, alias in pluginAlias.items():
        if pluginName in alias:
            return plugin
    return pluginName  # alias not found


loadAlias()
