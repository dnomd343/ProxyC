#!/usr/bin/env python3
# -*- coding: utf-8 -*-

Version = 'dev'

LogLevel = 'INFO'
LogFile = 'runtime.log'

ApiPath = '/'
ApiPort = 7839
ApiToken = ''

DnsServer = None
CheckThread = 64
WorkDir = '/tmp/ProxyC'
TestHost = 'proxyc.net'
TestSite = 'www.bing.com'
PathEnv = '/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin'

from Utils.Constant.LoadEnv import loadEnvOptions

for envKey, envValue in loadEnvOptions('../../env.yml').items():
    if type(envValue) == int:
        exec('%s = %s' % (envKey, envValue))
    if type(envValue) == str:
        exec('%s = \'%s\'' % (envKey, envValue))
