#!/usr/bin/python
# -*- coding:utf-8 -*-

import ProxyDecoder as Decoder

ssPlainUrl = 'ss://bf-cfb:test@192.168.100.1:8888'
ssCommonUrl = 'ss://YmYtY2ZiOnRlc3RAMTkyLjE2OC4xMDAuMTo4ODg4#example-server'
ssSip002Url = 'ss://cmM0LW1kNTpwYXNzd2Q@192.168.100.1:8888/?plugin=obfs-local%3Bobfs%3Dhttp#Example'

print(Decoder.decode(ssPlainUrl))
