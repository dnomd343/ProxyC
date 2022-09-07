#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import _thread
import argparse
import compileall
from Utils import Constant
from Utils.Exception import checkException


def parseArgs(rawArgs: list) -> argparse.Namespace:
    mainParser = argparse.ArgumentParser(description = 'Start running API server')
    mainParser.add_argument('--log', type = str, default = Constant.LogLevel, help = 'output log level')
    mainParser.add_argument('--dns', type = str, default = Constant.DnsServer, nargs = '+', help = 'specify dns server')
    mainParser.add_argument('--port', type = int, default = Constant.ApiPort, help = 'port for running')
    mainParser.add_argument('--path', type = str, default = Constant.ApiPath, help = 'root path for api server')
    mainParser.add_argument('--token', type = str, default = Constant.ApiToken, help = 'token for api server')
    mainParser.add_argument('--thread', type = int, default = Constant.CheckThread, help = 'number of check thread')
    mainParser.add_argument('-v', '--version', help = 'show version', action = 'store_true')
    return mainParser.parse_args(rawArgs)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'test':  # test mode
        from Test import runTest
        runTest(sys.argv[2:])
        sys.exit(0)

    mainArgs = parseArgs(sys.argv[1:])
    if mainArgs.version:  # output version and exit
        print('ProxyC version %s' % Constant.Version)
        sys.exit(0)
    Constant.LogLevel = mainArgs.log  # overwrite global options
    Constant.DnsServer = mainArgs.dns
    Constant.ApiPort = mainArgs.port
    Constant.ApiPath = mainArgs.path
    Constant.ApiToken = mainArgs.token
    Constant.CheckThread = mainArgs.thread


if __name__ == '__main__':
    from Utils.Check import Check
    from Utils import Api, DnsProxy
    from Utils.Logger import logger
    from Utils.Manager import Manager
    from concurrent.futures import ThreadPoolExecutor


def pythonCompile(dirRange: str = '/') -> None:  # python optimize compile
    for optimize in [-1, 1, 2]:
        compileall.compile_dir(dirRange, quiet = 1, optimize = optimize)
        logger.info('Python optimize compile -> %s (level = %i)' % (dirRange, optimize))


def runCheck(taskId: str, taskInfo: dict) -> None:
    success = True
    checkResult = {}
    try:
        checkResult = Check(taskId, taskInfo)  # check by task info
        logger.warning('[%s] Task finish' % taskId)
    except checkException as exp:
        success = False
        logger.error('[%s] Task error -> %s' % (taskId, exp))
    except:
        success = False
        logger.error('[%s] Task error -> Unknown error' % taskId)
    finally:
        if not success:  # got some error in check process
            taskInfo.pop('check')
            checkResult = {
                **taskInfo,
                'success': False,
            }
        Manager.finishTask(taskId, checkResult)  # commit check result


def loop(threadNum: int) -> None:
    logger.warning('Loop check start -> %i threads' % threadNum)
    threadPool = ThreadPoolExecutor(max_workers = threadNum)  # init thread pool
    while True:
        try:
            taskId, taskInfo = Manager.popTask()  # pop a task
            logger.warning('[%s] Load new task' % taskId)
        except:  # no more task
            time.sleep(2)
            continue
        threadPool.submit(runCheck, taskId, taskInfo)  # submit into thread pool


if __name__ == '__main__':
    logger.warning('ProxyC starts running (%s)' % Constant.Version)
    _thread.start_new_thread(pythonCompile, ('/usr',))  # python compile (generate .pyc file)
    _thread.start_new_thread(DnsProxy.start, (Constant.DnsServer, 53))  # start dns server
    _thread.start_new_thread(loop, (Constant.CheckThread, ))  # start check loop
    Api.startServer()  # start api server
