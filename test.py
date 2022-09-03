#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Basis import Constant
Constant.LogLevel = 'DEBUG'
from Basis.Logger import logging

from pprint import pprint
from Filter import Filter
from Decoder import Shadowsocks

ret = Shadowsocks.ssPlain('ss://aes-128-ctr:password@8.210.148.24:34326')
ret = Filter(ret['type'], ret['info'])
pprint(ret, sort_dicts = False)
