#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Utils import Constant
Constant.LogLevel = 'DEBUG'

import Decoder
from pprint import pprint
from Filter import Filter

# ret = Decoder.ss('ss://aes-128-ctr:pa@ss#word@8.210.148.24:34326#ok%2Bfuck')
# ret = Decoder.ss('ss://aes-128-ctr:pa@ss#word@fc00::1:34326#ok%2Bfuck')
# ret = Decoder.ss('ss://aes-128-ctr:pa@ss#word@[fc00::1]:34326#ok%2Bfuck')
# ret = Decoder.ss('ss://YmYtY2ZiOnRlc3QvIUAjOkAxOTIuMTY4LjEwMC4xOjg4ODg#example-server')
# ret = Decoder.sip002('ss://YWVzLTEyOC1nY206dGVzdA@192.168.100.1:8888#Example1')
# ret = Decoder.sip002('ss://2022-blake3-aes-256-gcm:YctPZ6U7xPPcU%2Bgp3u%2B0tx%2FtRizJN9K8y%2BuKlW2qjlI%3D@192.168.100.1:8888/?plugin=v2ray-plugin%3Bserver#Example3')

# ret = Decoder.ssr('ssr://ZmU4MDo6MTo2MDA0OmF1dGhfYWVzMTI4X21kNTphZXMtMjU2LWNmYjp0bHMxLjJfdGlja2V0X2F1dGg6Y0dGemMzZGsvP29iZnNwYXJhbT1ZMlUzTUdVeE5EY3dOekF1ZFhCa1lYUmxMbTFwWTNKdmMyOW1kQzVqYjIwJnByb3RvcGFyYW09TVRRM01EY3dPa0pGTTIxck9RJnJlbWFya3M9UlZoQlRWQk1SUSZncm91cD1kR1Z6ZEE')
# ret = Decoder.ssr('ssr://ZmU4MDo6MTo2MDA0OmF1dGhfYWVzMTI4X21kNTphZXMtMjU2LWNmYjp0bHMxLjJfdGlja2V0X2F1dGg6Y0dGemMzZGsvP3Byb3RvcGFyYW09')
# ret = Decoder.ssr('ssr://ZmU4MDo6MTo2MDA0OmF1dGhfYWVzMTI4X21kNTphZXMtMjU2LWNmYjp0bHMxLjJfdGlja2V0X2F1dGg6Y0dGemMzZGs')

# ret = Decoder.v2rayN('vmess://eyJhZGQiOiJmbnlkdXpheW92dnNxaTMyZ2kucTc1NDMudG9wIiwicHMiOiJ2MXzpppnmuK8wM3zljp_nlJ984piF4piF4piFICgyKSIsInNjeSI6ImF1dG8iLCJ0eXBlIjoiaHR0cCIsInNuaSI6IiIsInBhdGgiOiIvIiwicG9ydCI6MzgzMzcsInYiOjIsImhvc3QiOiJ4aGY0eHE3ZDVjYjRnc3kzeW1teWR3b2kuc2luYS5jbiIsInRscyI6IiIsImlkIjoiOTAxY2UyNTUtOTM2OS1kMWUyLTk1ODQtZGE1YTdqZjA1NDdrIiwibmV0IjoidGNwIiwiYWlkIjowfQ')
# ret = Decoder.v2rayN('vmess://ew0KICAidiI6ICIyIiwNCiAgInBzIjogIummmea4rzLnur8iLA0KICAiYWRkIjogIjExOS4yOC44OC4yMzAiLA0KICAicG9ydCI6ICI0NDMiLA0KICAiaWQiOiAiODRhOGU2ZDItMWFkMy00NjEyLTgzNjItYTdjMjNlOWU5MzEyIiwNCiAgImFpZCI6ICIwIiwNCiAgInNjeSI6ICJhdXRvIiwNCiAgIm5ldCI6ICJ3cyIsDQogICJ0eXBlIjogIm5vbmUiLA0KICAiaG9zdCI6ICJ0ZXN0LnNjdXRyb2JvdC5jb20iLA0KICAicGF0aCI6ICIvdm1lc3M/ZGVtbz10cnVlJmVkPTIwNDgmdGVzdD1vayIsDQogICJ0bHMiOiAidGxzIiwNCiAgInNuaSI6ICJoay5zY3V0cm9ib3QuY29tIiwNCiAgImFscG4iOiAiIg0KfQ==')

# ret = Decoder.vmess('vmess://901ce214-9369-d1e2-9584-da5a7ff0547d@pqxsiziyovtsqljrhq.q7543.top:38337/?type=tcp&encryption=auto&headerType=http&host=xhf4xq7d5cb4gsyjpmmydwoi.sina.cn&path=%2F#v1%7C%E9%A6%99%E6%B8%AF01%7CMPTCP%7C%E2%98%85%E2%98%85%E2%98%85%20%282%29')
# ret = Decoder.vmess('vmess://5f50d808-8281-45d9-a0c2-69e039099da7@119.28.88.230:443/?type=ws&encryption=auto&host=hk.scutrobot.com&path=%2Fvmess%3Fed%3D2048&security=tls&sni=hk.scutrobot.com#%E9%A6%99%E6%B8%AF2%E7%BA%BF')

ret = Decoder.vless('vless://f7a6a4c7-63a5-479e-818a-0555431e0219@119.28.88.230:443?encryption=none&flow=xtls-rprx-direct&security=xtls&sni=hk.scutrobot.com&type=tcp&headerType=none&host=hk.scutrobot.com#XTLS-%E9%A6%99%E6%B8%AFB')

# ret['info']['server'] = '[%s]' % ret['info']['server']

ret['info'] = Filter(ret['type'], ret['info'])
pprint(ret, sort_dicts = False)
