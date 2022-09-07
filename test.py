#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Utils import Constant
Constant.LogLevel = 'DEBUG'

import Decoder
from pprint import pprint
from Filter import Filter

# ret = Decoder.ssPlain('ss://aes-128-ctr:pa@ss#word@8.210.148.24:34326#ok%2Bfuck')
# ret = Decoder.ssPlain('ss://aes-128-ctr:pa@ss#word@fc00::1:34326#ok%2Bfuck')
# ret = Decoder.ssPlain('ss://aes-128-ctr:pa@ss#word@[fc00::1]:34326#ok%2Bfuck')
# ret = Decoder.ssCommon('ss://YmYtY2ZiOnRlc3QvIUAjOkAxOTIuMTY4LjEwMC4xOjg4ODg#example-server')
# ret = Decoder.sip002('ss://YWVzLTEyOC1nY206dGVzdA@192.168.100.1:8888#Example1')
# ret = Decoder.sip002('ss://2022-blake3-aes-256-gcm:YctPZ6U7xPPcU%2Bgp3u%2B0tx%2FtRizJN9K8y%2BuKlW2qjlI%3D@192.168.100.1:8888/?plugin=v2ray-plugin%3Bserver#Example3')

# ret = Decoder.ssr('ssr://ZmU4MDo6MTo2MDA0OmF1dGhfYWVzMTI4X21kNTphZXMtMjU2LWNmYjp0bHMxLjJfdGlja2V0X2F1dGg6Y0dGemMzZGsvP29iZnNwYXJhbT1ZMlUzTUdVeE5EY3dOekF1ZFhCa1lYUmxMbTFwWTNKdmMyOW1kQzVqYjIwJnByb3RvcGFyYW09TVRRM01EY3dPa0pGTTIxck9RJnJlbWFya3M9UlZoQlRWQk1SUSZncm91cD1kR1Z6ZEE')
# ret = Decoder.ssr('ssr://ZmU4MDo6MTo2MDA0OmF1dGhfYWVzMTI4X21kNTphZXMtMjU2LWNmYjp0bHMxLjJfdGlja2V0X2F1dGg6Y0dGemMzZGsvP3Byb3RvcGFyYW09')
# ret = Decoder.ssr('ssr://ZmU4MDo6MTo2MDA0OmF1dGhfYWVzMTI4X21kNTphZXMtMjU2LWNmYjp0bHMxLjJfdGlja2V0X2F1dGg6Y0dGemMzZGs')

ret = Decoder.v2rayN('vmess://eyJhZGQiOiJmbnlkdXpheW92dnNxaTMyZ2kucTc1NDMudG9wIiwicHMiOiJ2MXzpppnmuK8wM3zljp_nlJ984piF4piF4piFICgyKSIsInNjeSI6ImF1dG8iLCJ0eXBlIjoiaHR0cCIsInNuaSI6IiIsInBhdGgiOiIvIiwicG9ydCI6MzgzMzcsInYiOjIsImhvc3QiOiJ4aGY0eHE3ZDVjYjRnc3kzeW1teWR3b2kuc2luYS5jbiIsInRscyI6IiIsImlkIjoiOTAxY2UyNTUtOTM2OS1kMWUyLTk1ODQtZGE1YTdqZjA1NDdrIiwibmV0IjoidGNwIiwiYWlkIjowfQ')

# ret['info']['server'] = '[%s]' % ret['info']['server']

ret['info'] = Filter(ret['type'], ret['info'])
pprint(ret, sort_dicts = False)
