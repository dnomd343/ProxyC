#!/usr/bin/python
# -*- coding:utf-8 -*-

import ProxyDecoder as Decoder

ssPlainUrl = 'ss://bf-cfb:test@192.168.100.1:8888'
ssCommonUrl = 'ss://YmYtY2ZiOnRlc3RAMTkyLjE2OC4xMDAuMTo4ODg4#example-server'
ssSip002Url = 'ss://cmM0LW1kNTpwYXNzd2Q@192.168.100.1:8888/?plugin=obfs-local%3Bobfs%3Dhttp#Example'

ssrCommonUrl = 'ssr://ZmU4MDo6MTo2MDA0OmF1dGhfYWVzMTI4X21kNTphZXMtMjU2LWNmYjp0bHMxLjJfdGlja2V0X2F1dGg6Y0dGemMzZGsvP29iZnNwYXJhbT1ZMlUzTUdVeE5EY3dOekF1ZFhCa1lYUmxMbTFwWTNKdmMyOW1kQzVqYjIwJnByb3RvcGFyYW09TVRRM01EY3dPa0pGTTIxck9RJnJlbWFya3M9UlZoQlRWQk1SUSZncm91cD1kR1Z6ZEE'

print(Decoder.decode(ssrCommonUrl))
