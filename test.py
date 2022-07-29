#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
from threading import Thread
from Tester import Shadowsocks
from Tester import ShadowsocksR
from Basis.Logger import logging
from Basis.Functions import checkPortStatus


def waitForStart(port: int, times: int = 100, delay: int = 100) -> bool:
    for i in range(times):
        if not checkPortStatus(port):  # port occupied
            return True
        time.sleep(delay / 1000)  # default wait 100ms
    return False  # timeout


def test(testObj: dict) -> None:
    logging.warning(testObj['title'])
    testObj['client'].start()
    testObj['server'].start()
    if waitForStart(testObj['socks']['port']):
        logging.debug('client start complete')
    if waitForStart(testObj['interface']['port']):
        logging.debug('server start complete')
    logging.debug('start test process')

    time.sleep(1)

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


def runTest(testIter: iter, threadNum: int):
    threads = []
    while True:  # infinite loop
        try:
            for thread in threads:
                if thread.is_alive(): continue
                threads.remove(thread)  # remove dead thread
            if len(threads) < threadNum:
                for i in range(threadNum - len(threads)):  # start threads within limit
                    thread = Thread(target=test, args=(next(testIter),))  # create new thread
                    thread.start()
                    threads.append(thread)  # record thread info
            time.sleep(0.1)
        except StopIteration:  # traverse completed
            break
    for thread in threads:  # wait until all threads exit
        thread.join()


ss = Shadowsocks.load(isExtra = True)
ssr = ShadowsocksR.load()
logging.critical('test start')

runTest(ss, 64)
runTest(ssr, 64)

logging.critical('test complete')
