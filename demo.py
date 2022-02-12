#!/usr/bin/python
# -*- coding:utf-8 -*-

import ProxyFilter as Filter

info = {
    "type": "ss",
    "server": "127.0.0.1 ",
    "port": 12345,
    "password": "dnomd343",
    "method": "aes_256-ctr",
    "plugin": "obfs",
    "pluginParam": "obfs=http;host=www.bing.com"
}

print(Filter.filter(info))
