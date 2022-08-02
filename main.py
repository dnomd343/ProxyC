#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import _thread
from Basis import DnsProxy
from Basis.Check import Check
from Basis.Logger import logging
from Basis.Manager import Manager
from Basis.Api import startServer
from Basis.Constant import Version
from Basis.Compile import startCompile
from concurrent.futures import ThreadPoolExecutor

# dnsServers = None
dnsServers = ['223.5.5.5', '119.28.28.28']


def runCheck(taskId: str, taskInfo: dict) -> None:
    checkResult = Check(taskId, taskInfo)
    logging.warning('[%s] Task finish' % taskId)
    Manager.finishTask(taskId, checkResult)


def loopCheck(threadNum: int = 16) -> None:
    threadPool = ThreadPoolExecutor(max_workers = threadNum)
    while True:
        try:
            taskId, taskInfo = Manager.popTask()
            logging.warning('[%s] Load new task' % taskId)
        except:  # no more task
            time.sleep(2)
            continue
        threadPool.submit(runCheck, taskId, taskInfo)


logging.warning('ProxyC starts running (%s)' % Version)
_thread.start_new_thread(startCompile, ('/usr', ))  # python compile (generate .pyc file)
_thread.start_new_thread(DnsProxy.start, (dnsServers, 53))  # start dns server
_thread.start_new_thread(loopCheck, ())  # start loop check
startServer(apiToken = '')  # start api server
