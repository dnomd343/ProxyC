#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Basis import Constant
Constant.LogLevel = 'DEBUG'

import Decoder
from pprint import pprint
from Filter import Filter

# ret = Decoder.ssPlain('ss://aes-128-ctr:pa@ss#word@8.210.148.24:34326#ok%2Bfuck')
# ret = Decoder.ssCommon('ss://YmYtY2ZiOnRlc3QvIUAjOkAxOTIuMTY4LjEwMC4xOjg4ODg#example-server')
# ret = Decoder.sip002('ss://YWVzLTEyOC1nY206dGVzdA@192.168.100.1:8888#Example1')
ret = Decoder.sip002('ss://2022-blake3-aes-256-gcm:YctPZ6U7xPPcU%2Bgp3u%2B0tx%2FtRizJN9K8y%2BuKlW2qjlI%3D@192.168.100.1:8888/?plugin=v2ray-plugin%3Bserver#Example3')
ret = {
    'type': ret['type'],
    'name': ret['name'],
    'info': Filter(ret['type'], ret['info'])
}
pprint(ret, sort_dicts = False)
