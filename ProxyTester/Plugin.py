#!/usr/bin/python
# -*- coding:utf-8 -*-

import re
import json

gqConfig = {
    'key': 'dnomd343'
}

ckConfig = {
    'BypassUID': [
        'Q3iw2bAbC3KZvpm58XR6+Q=='
    ],
    'RedirAddr': 'www.bing.com',
    'PrivateKey': 'SFMUZ2g7e0jqzXXhBh5/rh/Odslnyu8A3LuZqH4ySVM='
}

pluginConfig = {
    'obfs-local': [
        {
            'caption': 'http mode',
            'server': '--plugin obfs-server --plugin-opts "obfs=http"',
            'client': '--plugin obfs-local --plugin-opts "obfs=http;obfs-host=www.bing.com"',
        },
        {
            'caption': 'tls mode',
            'server': '--plugin obfs-server --plugin-opts "obfs=tls"',
            'client': '--plugin obfs-local --plugin-opts "obfs=tls;obfs-host=www.bing.com"',
        },
        {
            'caption': 'http mode with URI',
            'server': '--plugin obfs-server --plugin-opts "obfs=http"',
            'client': '--plugin obfs-local --plugin-opts "obfs=http;obfs-host=www.bing.com;obfs-uri=/test"',
        },
        {
            'caption': 'http mode with POST method',
            'server': '--plugin obfs-server --plugin-opts "obfs=http"',
            'client': '--plugin obfs-local --plugin-opts "obfs=http;http-method=POST;obfs-host=www.bing.com"',
        }
    ],
    'simple-tls': [
        {
            'caption': 'basic mode',
            'server': '--plugin simple-tls --plugin-opts "s;n=$HOST"',
            'client': '--plugin simple-tls --plugin-opts "n=$HOST;no-verify"',
        },
        {
            'caption': 'with auth key',
            'server': '--plugin simple-tls --plugin-opts "s;n=$HOST;auth=dnomd343"',
            'client': '--plugin simple-tls --plugin-opts "n=$HOST;no-verify;auth=dnomd343"',
        },
        {
            'caption': 'wss mode',
            'server': '--plugin simple-tls --plugin-opts "s;n=$HOST;ws;ws-path=/test"',
            'client': '--plugin simple-tls --plugin-opts "n=$HOST;no-verify;ws;ws-path=/test"',
        }
    ],
    'v2ray-plugin': [
        {
            'caption': 'basic mode',
            'server': '--plugin v2ray-plugin --plugin-opts "server"',
            'client': '--plugin v2ray-plugin',
        },
        {
            'caption': 'basic with path',
            'server': '--plugin v2ray-plugin --plugin-opts "server;path=/test"',
            'client': '--plugin v2ray-plugin --plugin-opts "path=/test"',
        },
        {
            'caption': 'basic mode with tls',
            'server': '--plugin v2ray-plugin --plugin-opts "server;tls;host=$HOST;cert=$CERT;key=$KEY"',
            'client': '--plugin v2ray-plugin --plugin-opts "tls;host=$HOST"',
        },
        {
            'caption': 'quic mode',
            'server': '--plugin v2ray-plugin --plugin-opts "server;mode=quic;host=$HOST;cert=$CERT;key=$KEY"',
            'client': '--plugin v2ray-plugin --plugin-opts "mode=quic;host=$HOST"',
        }
    ],
    'xray-plugin': [
        {
            'caption': 'basic mode',
            'server': '--plugin xray-plugin --plugin-opts "server"',
            'client': '--plugin xray-plugin',
        },
        {
            'caption': 'basic mode with tls',
            'server': '--plugin xray-plugin --plugin-opts "server;tls;host=$HOST;cert=$CERT;key=$KEY"',
            'client': '--plugin xray-plugin --plugin-opts "tls;host=$HOST"',
        },
        {
            'caption': 'quic mode',
            'server': '--plugin xray-plugin --plugin-opts "server;mode=quic;host=$HOST;cert=$CERT;key=$KEY"',
            'client': '--plugin xray-plugin --plugin-opts "mode=quic;host=$HOST"',
        },
        {
            'caption': 'grpc mode',
            'server': '--plugin xray-plugin --plugin-opts "server;mode=grpc;host=$HOST;cert=$CERT;key=$KEY"',
            'client': '--plugin xray-plugin --plugin-opts "mode=grpc"',
        },
        {
            'caption': 'grpc mode with tls',
            'server': '--plugin xray-plugin --plugin-opts "server;tls;mode=grpc;host=$HOST;cert=$CERT;key=$KEY"',
            'client': '--plugin xray-plugin --plugin-opts "tls;mode=grpc;host=$HOST"',
        }
    ],
    'kcptun-client': [
        {
            'caption': 'basic mode',
            'server': '--plugin kcptun-server',
            'client': '--plugin kcptun-client',
        },
        {
            'caption': 'with nocomp',
            'server': '--plugin kcptun-server --plugin-opts "nocomp"',
            'client': '--plugin kcptun-client --plugin-opts "nocomp"',
        },
        {
            'caption': 'with key',
            'server': '--plugin kcptun-server --plugin-opts "key=dnomd343"',
            'client': '--plugin kcptun-client --plugin-opts "key=dnomd343"',
        },
        {
            'caption': 'fast3 mode with twofish crypt',
            'server': '--plugin kcptun-server --plugin-opts "crypt=twofish;mode=fast3"',
            'client': '--plugin kcptun-client --plugin-opts "crypt=twofish;mode=fast3"',
        }
    ],
    'gost-plugin': [
        {
            'caption': 'ws mode',
            'server': '--plugin gost-plugin --plugin-opts "server;mode=ws"',
            'client': '--plugin gost-plugin --plugin-opts "mode=ws"',
        },
        {
            'caption': 'mws mode',
            'server': '--plugin gost-plugin --plugin-opts "server;mode=mws"',
            'client': '--plugin gost-plugin --plugin-opts "mode=mws;mux=1"',
        },
        {
            'caption': 'tls mode',
            'server': '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=tls"',
            'client': '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=tls"',
        },
        {
            'caption': 'xtls mode',
            'server': '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=xtls"',
            'client': '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=xtls"',
        },
        {
            'caption': 'mtls mode',
            'server': '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=mtls"',
            'client': '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=mtls;mux=1"',
        },
        {
            'caption': 'h2 mode',
            'server': '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=h2"',
            'client': '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=h2"',
        },
        {
            'caption': 'wss mode',
            'server': '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=wss"',
            'client': '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=wss"',
        },
        {
            'caption': 'mwss mode',
            'server': '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=mwss"',
            'client': '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=mwss;mux=1"',
        },
        {
            'caption': 'quic mode',
            'server': '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=quic"',
            'client': '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=quic"',
        },
        {
            'caption': 'grpc mode',
            'server': '--plugin gost-plugin --plugin-opts "server;cert=$CERT;key=$KEY;mode=grpc"',
            'client': '--plugin gost-plugin --plugin-opts "serverName=$HOST;mode=grpc"',
        }
    ],
    'ck-client': [
        {
            'caption': 'basic mode',
            'server': '--plugin ck-server --plugin-opts "$CONFIG"',
            'client': '--plugin ck-client --plugin-opts "UID=Q3iw2bAbC3KZvpm58XR6+Q==;'
                      'PublicKey=xTbqKW4Sg/xjDXDhys26ChXUQSrgxO+mBflTUeQpfWQ=;'
                      'ServerName=www.bing.com;BrowserSig=chrome;'
                      'NumConn=4;EncryptionMethod=plain;StreamTimeout=300"',
        }
    ],
    'gq-client': [
        {
            'caption': 'basic mode',
            'server': '--plugin gq-server --plugin-opts "$CONFIG"',
            'client': '--plugin gq-client --plugin-opts "ServerName=www.bing.com;'
                      'key=dnomd343;TicketTimeHint=300;Browser=chrome"',
        }
    ],
    'mtt-client': [
        {
            'caption': 'basic mode',
            'server': '--plugin mtt-server --plugin-opts "cert=$CERT;key=$KEY"',
            'client': '--plugin mtt-client --plugin-opts "n=$HOST"',
        },
        {
            'caption': 'wss mode',
            'server': '--plugin mtt-server --plugin-opts "wss;cert=$CERT;key=$KEY"',
            'client': '--plugin mtt-client --plugin-opts "wss;n=$HOST"',
        },
        {
            'caption': 'wss mode with path',
            'server': '--plugin mtt-server --plugin-opts "wss;wss-path=/test;cert=$CERT;key=$KEY"',
            'client': '--plugin mtt-client --plugin-opts "wss;wss-path=/test;n=$HOST"',
        }
    ],
    'qtun-client': [
        {
            'caption': 'basic mode',
            'server': '--plugin qtun-server --plugin-opts "cert=$CERT;key=$KEY"',
            'client': '--plugin qtun-client --plugin-opts "host=$HOST"',
        }
    ],
    'gun-plugin': [
        {
            'caption': 'basic mode',
            'server': '--plugin gun-plugin --plugin-opts "server:cleartext"',
            'client': '--plugin gun-plugin --plugin-opts "client:cleartext"',
        },
        {
            'caption': 'basic mode with tls',
            'server': '--plugin gun-plugin --plugin-opts "server:$CERT:$KEY"',
            'client': '--plugin gun-plugin --plugin-opts "client:$HOST"',
        }
    ]
}

def loadPluginConfig(plugin: str, host: str, cert: str, key: str) -> list: # without rabbit-tcp
    result = []
    filePath = None
    fileContent = None
    if plugin == 'ck-client': # Cloak
        filePath = '/tmp/ck-test.json'
        fileContent = json.dumps(ckConfig)
    if plugin == 'gq-client': # GoQuiet
        filePath = '/tmp/gq-test.json'
        fileContent = json.dumps(gqConfig)

    for pluginInfo in pluginConfig[plugin]:
        pluginInfo['server'] = pluginInfo['server'].replace('$HOST', host).replace('$CERT', cert).replace('$KEY', key)
        pluginInfo['client'] = pluginInfo['client'].replace('$HOST', host).replace('$CERT', cert).replace('$KEY', key)
        if filePath is not None:
            pluginInfo['server'] = pluginInfo['server'].replace('$CONFIG', filePath)

        content = re.search(r'^--plugin ([\s\S]*) --plugin-opts "([\s\S]*)"$', pluginInfo['server'])
        if content is None:
            content = re.search(r'^--plugin ([\s\S]*)$', pluginInfo['server'])
            serverOption = {
                'type': content[1],
                'param': ''
            }
        else:
            serverOption = {
                'type': content[1],
                'param': content[2]
            }
        content = re.search(r'^--plugin ([\s\S]*) --plugin-opts "([\s\S]*)"$', pluginInfo['client'])
        if content is None:
            content = re.search(r'^--plugin ([\s\S]*)$', pluginInfo['client'])
            clientOption = {
                'type': content[1],
                'param': ''
            }
        else:
            clientOption = {
                'type': content[1],
                'param': content[2]
            }

        result.append({
            'caption': pluginInfo['caption'],
            'server': serverOption,
            'client': clientOption,
            'file': fileContent,
            'path': filePath
        })
    return result
