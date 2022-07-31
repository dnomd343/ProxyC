#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from Builder import Builder
from Basis.Logger import logging

proxySS = {
    'server': '127.0.0.1',
    'port': 12345,
    'passwd': 'dnomd343',
    'method': 'aes-128-ctr',
    'plugin': None
}

proxySSR = {
    'server': '127.0.0.1',
    'port': 12345,
    'passwd': 'dnomd343',
    'method': 'aes-128-ctr',
    'protocol': 'origin',
    'protocolParam': '',
    'obfs': 'plain',
    'obfsParam': '',
}

proxyVMess = {
    'server': '127.0.0.1',
    'port': 12345,
    'method': 'auto',
    'id': '614d3a56-8a04-4c65-88a2-45896f0bd13c',
    'aid': 0,
    'stream': {
        'type': 'tcp',
        'obfs': None,
        'secure': {
            'sni': '343.re',
            'alpn': None,
            'verify': True,
        },
    }
}

proxyVLESS = {
    'server': '127.0.0.1',
    'port': 12345,
    'method': 'none',
    'id': '614d3a56-8a04-4c65-88a2-45896f0bd13c',
    'stream': {
        'type': 'tcp',
        'obfs': None,
        'secure': {
            'type': 'xtls',
            'sni': '343.re',
            'alpn': None,
            'verify': True,
            'flow': 'xtls-direct',
            'udp443': False
        },
    }
}

proxyTrojan = {
    'server': '127.0.0.1',
    'port': 12345,
    'passwd': 'dnomd343',
    'stream': {
        'type': 'tcp',
        'obfs': None,
        'secure': {
            'type': 'tls',
            'sni': '343.re',
            'alpn': None,
            'verify': True,
        },
    }
}

proxyTrojanGo = {
    'server': '127.0.0.1',
    'port': 12345,
    'passwd': 'dnomd343',
    'sni': '343.re',
    'alpn': None,
    'verify': True,
    'ws': {
        'host': '343.re',
        'path': '/test',
    },
    'ss': {
        'method': 'AES-128-GCM',
        'passwd': 'dnomd343',
    },
    'plugin': {
        'type': 'obfs-local',
        'param': 'obfs=http;obfs-host=www.bing.com'
    },
}

proxyBrook = {
    'server': '::1',
    'port': 12345,
    'passwd': 'dnomd343',
    'stream': {
        'type': 'ws',
        'host': '343.re',
        'path': '/test',
        'raw': True,
        'secure': {
            'verify': False
        },
    }
}

# client = Builder('ss', proxySS)
# client = Builder('ssr', proxySSR)
# client = Builder('vmess', proxyVMess)
# client = Builder('vless', proxyVLESS)
# client = Builder('trojan', proxyTrojan)
# client = Builder('trojan-go', proxyTrojanGo)
client = Builder('brook', proxyBrook)

logging.critical(client.id)
logging.critical(client.proxyType)
logging.critical(client.proxyInfo)
logging.critical(client.socksAddr)
logging.critical(client.socksPort)

time.sleep(15)
logging.critical(client.status())

client.destroy()
logging.critical(client.status())
logging.critical('Client output:\n' + str(client.output))
