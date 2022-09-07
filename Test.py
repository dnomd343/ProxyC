#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
from Utils import Constant


def parseArgs(rawArgs: list) -> argparse.Namespace:
    testParser = argparse.ArgumentParser(description = 'Test that each function is working properly')
    testParser.add_argument('PROTOCOL', type = str, help = 'test protocol name')
    testParser.add_argument('-a', '--all', help = 'test extra shadowsocks items', action = 'store_true')
    testParser.add_argument('-6', '--ipv6', help = 'test on ipv6 network', action = 'store_true')
    testParser.add_argument('--debug', help = 'enable debug log level', action = 'store_true')
    testParser.add_argument('--url', type = str, default = 'http://google.com', help = 'http request url')
    testParser.add_argument('--cert', type = str, default = '', help = 'specify the certificate id')
    testParser.add_argument('--thread', type = int, default = 16, help = 'thread number in check process')
    testParser.add_argument('--select', type = str, nargs = '+', help = 'select id list for test')
    return testParser.parse_args(rawArgs)


def initTest(args: list) -> argparse.Namespace:
    if len(args) == 0 or args[0].startswith('-'):  # no protocol is specified
        args = ['all'] + args  # test all items
    testArgs = parseArgs(args)
    Constant.LogLevel = 'debug' if testArgs.debug else 'warning'

    from Tester import testEntry
    from Utils.Logger import logger  # load logger after setting up LogLevel
    from Utils.Tester import loadBind, loadCert
    if testArgs.PROTOCOL != 'all' and testArgs.PROTOCOL not in testEntry:
        logger.error('Unknown protocol -> %s' % testArgs.PROTOCOL)
        sys.exit(1)

    loadBind(serverV6 = testArgs.ipv6, clientV6 = testArgs.ipv6)  # ipv4 / ipv6 (127.0.0.1 / ::1)
    loadCert(certId = testArgs.cert)  # certificate config
    logger.critical('TEST ITEM: %s' % testArgs.PROTOCOL)
    logger.critical('SELECT: ' + str(testArgs.select))
    logger.critical('URL: %s' % testArgs.url)
    logger.critical('THREAD NUMBER: %i' % testArgs.thread)
    return testArgs


def runTest(args: list) -> None:  # run test process
    testArgs = initTest(args)
    from Tester import testEntry
    from Utils.Tester import Test
    from Utils.Logger import logger

    logger.critical('-' * 32 + ' TEST START ' + '-' * 32)  # test start
    if testArgs.PROTOCOL == 'all':  # run all test items
        for item in testEntry:
            if item == ('ss' if testArgs.all else 'ss-all'):  # skip ss / ss-all
                continue
            logger.critical('TEST ITEM -> ' + item)
            Test(testEntry[item], testArgs.thread, testArgs.url, testArgs.select)
    else:  # run single item
        if testArgs.PROTOCOL == 'ss' and testArgs.all:  # test shadowsocks extra items
            testArgs.PROTOCOL = 'ss-all'
        Test(testEntry[testArgs.PROTOCOL], testArgs.thread, testArgs.url, testArgs.select)
    logger.critical('-' * 32 + ' TEST COMPLETE ' + '-' * 32)  # test complete


if __name__ == '__main__':
    runTest(sys.argv[1:])
