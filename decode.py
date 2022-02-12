#!/usr/bin/python
# -*- coding:utf-8 -*-

commonUrl = 'ss://YmYtY2ZiOnRlc3RAMTkyLjE2OC4xMDAuMTo4ODg4#example-server'
sip002Url = 'ss://cmM0LW1kNTpwYXNzd2Q@192.168.100.1:8888/?plugin=obfs-local%3Bobfs%3Dhttp#Example'

import ProxyDecoder as Decoder

# print(Decoder.decode(commonUrl))
print(Decoder.decode(sip002Url))
