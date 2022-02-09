#!/usr/bin/python
# -*- coding:utf-8 -*-

import test.Shadowsocks as ss
import test.ShadowsocksR as ssr

def Shadowsocks(port, password):
    return ss.test(port, password)

def ShadowsocksR(port, password):
    return ssr.test(port, password)
