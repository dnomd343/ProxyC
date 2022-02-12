#!/usr/bin/python
# -*- coding:utf-8 -*-

import ProxyFilter as Filter

ssInfo = {
    "type": "ss",
    "server": "127.0.0.1 ",
    "port": 12345,
    "password": "dnomd343",
    "method": "aes_256-ctr",
    "plugin": "obfs",
    "pluginParam": "obfs=http;host=www.bing.com"
}

ssrInfo = {
    "type": "ssr",
    "server": "  127.0.0.1",
    "port": 23456,
    "password": "dnomd343",
    "method": "table",
    "protocol": "auth-aes128_md5",
    "protocolParam": "",
    "obfs": "",
    "obfsParam": "fafadfaf"
}

print(Filter.filter(ssrInfo))
