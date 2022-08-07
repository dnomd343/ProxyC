#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import copy
import time
import _thread
import argparse
import compileall
from Basis import Constant


def mainArgParse(rawArgs: list) -> argparse.Namespace:
    mainParser = argparse.ArgumentParser(description = 'Start running API server')
    mainParser.add_argument('--log', type = str, default = 'debug', help = 'output log level')
    mainParser.add_argument('--port', type = int, default = 7839, help = 'port for running')
    mainParser.add_argument('--token', type = str, default = '', help = 'token for api server')
    mainParser.add_argument('-v', '--version', help = 'show version', action = 'store_true')
    # TODO: api path / dns server
    return mainParser.parse_args(rawArgs)


def testArgParse(rawArgs: list) -> argparse.Namespace:
    testParser = argparse.ArgumentParser(description = 'Test that each function is working properly')
    testParser.add_argument('PROTOCOL', type = str, help = 'test protocol name')
    testParser.add_argument('-a', '--all', help = 'test extra shadowsocks items', action = 'store_true')
    testParser.add_argument('-6', '--ipv6', help = 'test on ipv6 network', action = 'store_true')
    testParser.add_argument('--url', type = str, default = 'http://baidu.com', help = 'http request url')
    testParser.add_argument('--cert', type = str, help = 'specify the certificate id')
    testParser.add_argument('--thread', type = int, default = 16, help = 'thread number in check process')
    testParser.add_argument('--select', type = str, nargs = '+', help = 'select id list for test')
    return testParser.parse_args(rawArgs)


inputArgs = copy.copy(sys.argv)
if len(inputArgs) >= 0:  # remove first arg (normally file name)
    inputArgs.pop(0)
if len(inputArgs) != 0 and inputArgs[0].lower() == 'test':  # test mode
    inputArgs.pop(0)  # remove `test`
    if len(inputArgs) == 0 or inputArgs[0].startswith('-'):  # no protocol is specified
        inputArgs = ['all'] + inputArgs
    testArgs = testArgParse(inputArgs)
    print(testArgs)
    sys.exit(1)
    # TODO: start test process
else:
    mainArgs = mainArgParse(inputArgs)
    if mainArgs.version:  # output version and exit
        print('ProxyC version -> %s' % Constant.Version)
        sys.exit(0)
    Constant.LogLevel = mainArgs.log  # overwrite global options
    Constant.ApiPort = mainArgs.port
    Constant.ApiToken = mainArgs.token


from Basis.Check import Check
from Basis import Api, DnsProxy
from Basis.Logger import logging
from Basis.Manager import Manager
from concurrent.futures import ThreadPoolExecutor


def pythonCompile(dirRange: str = '/') -> None:  # python optimize compile
    for optimize in [-1, 1, 2]:
        compileall.compile_dir(dirRange, quiet = 1, optimize = optimize)
        logging.warning('Python optimize compile -> %s (level = %i)' % (dirRange, optimize))


def runCheck(taskId: str, taskInfo: dict) -> None:
    checkResult = Check(taskId, taskInfo)  # check by task info
    logging.warning('[%s] Task finish' % taskId)
    Manager.finishTask(taskId, checkResult)  # commit check result


def loop(threadNum: int = 16) -> None:
    threadPool = ThreadPoolExecutor(max_workers = threadNum)  # init thread pool
    while True:
        try:
            taskId, taskInfo = Manager.popTask()  # pop a task
            logging.warning('[%s] Load new task' % taskId)
        except:  # no more task
            time.sleep(2)
            continue
        threadPool.submit(runCheck, taskId, taskInfo)  # submit into thread pool


logging.warning('ProxyC starts running (%s)' % Constant.Version)
_thread.start_new_thread(pythonCompile, ('/usr',))  # python compile (generate .pyc file)
_thread.start_new_thread(DnsProxy.start, (Constant.DnsServer, 53))  # start dns server
_thread.start_new_thread(loop, ())  # start check loop
Api.startServer()  # start api server
