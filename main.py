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

# dnsServers = None
dnsServers = ['223.5.5.5', '119.28.28.28']


def runCheck() -> None:  # try to pop a task and check
    try:
        taskId, taskInfo = Manager.popTask()
        logging.warning('[%s] Load new task' % taskId)
    except:
        return  # no more task
    checkResult = Check(taskId, taskInfo)
    logging.warning('[%s] Task finish' % taskId)
    Manager.finishTask(taskId, checkResult)


def loopCheck() -> None:
    while True:  # TODO: thread pool working
        runCheck()
        time.sleep(2)


logging.warning('ProxyC starts running (%s)' % Version)
_thread.start_new_thread(startCompile, ('/usr', ))  # python compile (generate .pyc file)
_thread.start_new_thread(DnsProxy.start, (dnsServers, 53))  # start dns server
_thread.start_new_thread(loopCheck, ())  # start loop check
startServer(apiToken = '')  # start api server
