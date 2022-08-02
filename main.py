#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import _thread
import subprocess
from Basis.Logger import logging
from Basis.Api import startServer
from Basis.Constant import Version
from Basis.Compile import startCompile

dnsServers = None
# dnsServers = ['223.5.5.5', '119.28.28.28']


def startDnsproxy(command: list) -> subprocess.Popen:
    logging.debug('start dnsproxy -> %s' % command)
    return subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)


def daemonDnsproxy(servers: list or None, port: int = 53, cache: int = 4194304) -> None:  # default cache size -> 4MiB
    if servers is None or len(servers) == 0:
        logging.info('skip dnsproxy process')
        return
    logging.info('start dnsproxy at port %i -> %s' % (port, servers))
    os.system('echo "nameserver 127.0.0.1" > /etc/resolv.conf')  # system dns settings
    dnsCommand = [
        'dnsproxy', '--all-servers',
        '--port', str(port),
        '--cache', '--cache-size', str(cache)
    ]
    for server in servers:
        dnsCommand += ['--upstream', server]
    dnsproxy = startDnsproxy(dnsCommand)
    while True:
        time.sleep(2)  # daemon time gap
        if dnsproxy.poll() is not None:  # unexpected exit
            logging.warning('dnsproxy unexpected exit')
            logging.debug('output of dnsproxy\n%s' % dnsproxy.stdout.read().decode('utf-8'))
            dnsproxy = startDnsproxy(dnsCommand)


from Basis.Check import Check
from Basis.Manager import Manager

def loopCheck() -> None:
    while True:
        time.sleep(2)  # TODO: thread pool working
        try:
            taskId, taskInfo = Manager.popTask()
        except:
            logging.debug('no more task')
            continue
        logging.info('new task %s -> %s' % (taskId, taskInfo))
        ret = Check(taskId, taskInfo)
        logging.info('check result -> %s' % ret)
        Manager.finishTask(taskId, ret)


logging.warning('ProxyC starts running (%s)' % Version)
_thread.start_new_thread(startCompile, ('/usr', ))  # python compile (generate .pyc file)
_thread.start_new_thread(daemonDnsproxy, (dnsServers, 53))  # set system's dns server
_thread.start_new_thread(loopCheck, ())  # start loop check
startServer(apiToken = '')  # start api server
