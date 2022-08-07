#!/usr/bin/env python

from pprint import pprint
from Filter import Filter

ssProxy = {
    'server': '1.1.1.1',
    'port': '12345',
    'method': 'none',
    'passwd': 'dnomd343',
    'plugin': {
        'type': 'obfs'
    }
}

ssrProxy = {
    'server': '1.1.1.1',
    'port': 12345,
    'method': 'table',
    'passwd': 'dnomd343',
    'protocol': 'auth_chain-a',
    'protocolParam': '123',
    'obfs': 'plain',
    'obfsParam': 'ok',
}

vmessProxy = {
    'server': '1.1.1.1',
    'port': b'12345',
    'id': 'c8783403-64d5-4b6d-8cf4-bd3988d01b6c',
    'aid': '64',
    'stream': {
        'type': 'GRPC',
        'service': 'no-gfw',
        'mode': '  multi  ',
        'secure': {
            'sni': '',
            'alpn': 'h2,   http/1.1',
            'verify': 'False  '
        }
    }
}

vlessProxy = {
    'server': '1.1.1.1',
    'port': r'12345',
    'method': 'NONE',
    'id': '  3f163adf-5bdd-40d0-b0ec-e47f9bebcac7',
    'stream': {
        'type': 'grpc',
        'service': 'dnomd343',
        # 'secure': None,
        # 'secure': {
        #     'type': 'tls',
        #     'sni': '23333',
        #     'alpn': 'h2',
        #     'verify': 0
        # }
        # 'secure': {
        #     'type': 'xtls',
        #     'sni': '23333',
        #     'alpn': 'h2',
        #     'verify': True,
        #     'flow': 'xtls-rprx-direct',
        #     'udp443': 0.1
        # }
    }
}

trojanProxy = {
    'server': 'www.dnomd343.top',
    'port': 12345,
    'passwd': b'dnomd343',
    'stream': {
        # 'type': 'grpc',
        'type': 'h2',
        # 'host': '343.re',
        'service': 'dnomd343',
        # 'secure': None,
        'secure': {
            'type': 'tls',
            'sni': '',
            'alpn': 'h2',
            'verify': 0
        }
        # 'secure': {
        #     'type': 'xtls',
        #     'sni': '23333',
        #     'alpn': 'h2',
        #     'verify': True,
        #     'flow': 'xtls-rprx-direct',
        #     'udp443': 0.1
        # }
    }
}

trojanGoProxy = {
    'server': '343.re',
    'port': 12345,
    'passwd': 'dnomd343',
    'sni': '',
    'alpn': ' h2',
    'verify': 'FALSE',
    'ws': {
        'host': 'dnomd343.top',
        'path': '/test',
    },
    'ss': {
        'method': 'chacha20-ietf-poly1305',
        'passwd': 'dnomd343',
    },
    'plugin': {
        'type': 'go-quiet',
        'param': 123
    }
}

brookProxy = {
    'server': '1.1.1.1',
    'port': 12345,
    'passwd': 'dnomd343',
    'stream': {
        'type': 'ws',
        'host': '343.re',
        'path': '/test',
        'raw': True,
        'secure': {
            'verify': '  0'
        }
    },
}

hysteriaProxy = {
    'server': 'www.343.re',
    'port': 12345,
    'protocol': 'faketcp',
    'obfs': '1234',
    'passwd': 'dnomd343',
    'up': 100,
    'down': 500,
    'sni': '',
    'alpn': 'h3',
    'verify': 'FALSE',
}

# ret = Filter('ss', ssProxy)
# ret = Filter('ssr', ssrProxy)
# ret = Filter('vmess', vmessProxy)
# ret = Filter('vless', vlessProxy)
# ret = Filter('trojan', trojanProxy)
# ret = Filter('trojan-go', trojanGoProxy)
# ret = Filter('brook', brookProxy)
ret = Filter('hysteria', hysteriaProxy)
pprint(ret, sort_dicts = False)
