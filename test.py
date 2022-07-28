#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
from threading import Thread
from Tester import Shadowsocks
from Basis.Logger import logging

testDelay = 1  # wait 1s before request test
threadNum = 128  # thread number

def test(testObj: dict) -> None:
    logging.warning(testObj['title'])
    testObj['client'].start()
    testObj['server'].start()
    time.sleep(testDelay)
    errFlag = False
    try:
        request = requests.get(
            'http://iserv.scutbot.cn',
            proxies = {
                'http': 'socks5://127.0.0.1:%i' % testObj['socks']['port'],
                'https': 'socks5://127.0.0.1:%i' % testObj['socks']['port'],
            },
            timeout = 10
        )
        request.raise_for_status()
        logging.info('socks5 127.0.0.1:%i -> ok' % testObj['socks']['port'])
    except Exception as exp:
        logging.error('socks5 127.0.0.1:%i -> error' % testObj['socks']['port'])
        logging.error('requests exception\n' + str(exp))
        errFlag = True

    testObj['client'].quit()
    testObj['server'].quit()
    if errFlag:
        logging.warning('client info')
        logging.error('command -> %s' % testObj['client'].cmd)
        logging.error('envVar -> %s' % testObj['client'].env)
        logging.error('file -> %s' % testObj['client'].file)
        logging.warning('client capture output')
        logging.error('\n' + str(testObj['client'].output))
        logging.warning('server info')
        logging.error('command -> %s' % testObj['server'].cmd)
        logging.error('envVar -> %s' % testObj['server'].env)
        logging.error('file -> %s' % testObj['server'].file)
        logging.warning('server capture output')
        logging.error('\n' + str(testObj['server'].output))


threads = []
ss = Shadowsocks.load(isExtra = True)

while True:
    try:
        for i in range(threadNum):
            thread = Thread(target = test, args = (next(ss),))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()
        threads.clear()
    except StopIteration:
        break
for thread in threads:
    thread.join()

logging.critical('test complete')
