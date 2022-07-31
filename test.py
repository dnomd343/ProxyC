#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import Tester
from Tester import testEntry
from Basis.Logger import logging

threadNum = 16
testItem = None
testFilter = None
testUrl = 'http://baidu.com'
helpMsg = '''
  ./test.py [ITEM] [OPTIONS]

    [ITEM]: ss / ss-all / ssr / vmess / vless / trojan / trojan-go / brook / hysteria

    [OPTIONS]:
      --thread NUM             thread number
      --url URL                http check url
      --filter ID1[,ID2...]    test the specified id
      --all                    test extra shadowsocks items
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

logging.critical('test item: ' + ('all' if testItem is None else testItem))
logging.critical('filter: %s' % testFilter)
logging.critical('url: ' + testUrl)
logging.critical('thread number: %i' % threadNum)
logging.critical('TEST START')
if testItem is not None:
    Tester.test(testEntry[testItem], threadNum, testUrl, testFilter)
else:
    for item in testEntry:
        if item == ('ss' if '--all' in sys.argv else 'ss-all'):  # skip ss / ss-all
            continue
        logging.critical('TEST ITEM -> ' + item)
        Tester.test(testEntry[item], threadNum, testUrl, testFilter)
logging.critical('TEST COMPLETE')
