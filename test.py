#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
from Tester import Shadowsocks
from Basis.Logger import logging
from Basis.Functions import networkStatus

def test(testObj: dict) -> None:
    logging.warning(testObj['title'])
    logging.debug('network status -> %s' % networkStatus())
    testObj['client'].start()
    testObj['server'].start()

    time.sleep(1)

    errFlag = False
    try:
        request = requests.get(
            'http://baidu.com',
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
        logging.error('command -> ' + str(testObj['client'].cmd))
        logging.error('envVar -> ' + str(testObj['client'].env))
        logging.error('file -> ' + str(testObj['client'].file))
        logging.warning('client capture output')
        logging.error('\n' + str(testObj['client'].output))
        logging.warning('server info')
        logging.error('command -> ' + str(testObj['server'].cmd))
        logging.error('envVar -> ' + str(testObj['server'].env))
        logging.error('file -> ' + str(testObj['server'].file))
        logging.warning('server capture output')
        logging.error('\n' + str(testObj['server'].output))


testList = Shadowsocks.load(isExtra = True)
for testObject in testList:
    test(testObject)
