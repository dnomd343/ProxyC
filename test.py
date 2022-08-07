#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from Tester import testEntry
from Basis.Logger import logging
from Basis.Test import Test, loadBind, loadCert

threadNum = 16
testItem = None
testFilter = None
testUrl = 'http://baidu.com'
helpMsg = '''
  ./test.py [ITEM] [OPTIONS]

    [ITEM]: ss / ssr / vmess / vless / trojan / trojan-go / brook / hysteria

    [OPTIONS]:
      --thread NUM             thread number
      --url URL                http check url
      --filter ID1[,ID2...]    test the specified id
      --all                    test extra shadowsocks items
      --ipv6                   test on ipv6 network
      --help                   show this message
'''


def getArg(field: str) -> str or None:
    try:
        index = sys.argv.index(field)
        return sys.argv[index + 1]
    except:
        return None


if '--help' in sys.argv:
    print(helpMsg)
    sys.exit(0)
if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
    testItem = sys.argv[1]
if getArg('--url') is not None:
    testUrl = getArg('--url')
if getArg('--thread') is not None:
    threadNum = int(getArg('--thread'))
if getArg('--filter') is not None:
    testFilter = set(getArg('--filter').split(','))

isV6 = '--ipv6' in sys.argv
loadBind(serverV6 = isV6, clientV6 = isV6)  # ipv4 / ipv6 (127.0.0.1 / ::1)
loadCert('proxyc.net')  # default cert config
logging.critical('TEST ITEM: ' + ('all' if testItem is None else testItem))
logging.critical('FILTER: %s' % testFilter)
logging.critical('URL: ' + testUrl)
logging.critical('THREAD NUMBER: %i' % threadNum)

logging.critical('-------------------------------- TEST START --------------------------------')
if testItem is not None:
    if testItem == 'ss' and '--all' in sys.argv:
        testItem = 'ss-all'
    Test(testEntry[testItem], threadNum, testUrl, testFilter)
else:
    for item in testEntry:
        if item == ('ss' if '--all' in sys.argv else 'ss-all'):  # skip ss / ss-all
            continue
        logging.critical('TEST ITEM -> ' + item)
        Test(testEntry[item], threadNum, testUrl, testFilter)
logging.critical('-------------------------------- TEST COMPLETE --------------------------------')
