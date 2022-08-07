#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import _thread
import compileall
from Basis import Constant
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


def loopCheck(threadNum: int = 16) -> None:
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
_thread.start_new_thread(pythonCompile, ('/usr', ))  # python compile (generate .pyc file)
_thread.start_new_thread(DnsProxy.start, (Constant.DnsServer, 53))  # start dns server
_thread.start_new_thread(loopCheck, ())  # start loop check
Api.startServer(apiToken = Constant.ApiToken)  # start api server
