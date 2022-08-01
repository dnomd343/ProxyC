#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import _thread
import subprocess
from Basis.Logger import logging
from Basis.Api import startServer
from Basis.Constant import Version
from Basis.Compile import startCompile


def startDnsproxy(command: list) -> subprocess.Popen:
    logging.debug('start dnsproxy -> %s' % command)
    return subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)


def daemonDnsproxy(dnsServers: list, localPort: int = 53, cacheSize: int = 4194304) -> None:  # default cache -> 4MiB
    logging.info('start dnsproxy at port %i -> %s' % (localPort, dnsServers))
    dnsCommand = [
        'dnsproxy', '--all-servers',
        '--port', str(localPort),
        '--cache', '--cache-size', str(cacheSize)
    ]
    for dnsServer in dnsServers:
        dnsCommand += ['--upstream', dnsServer]
    dnsproxy = startDnsproxy(dnsCommand)
    while True:
        time.sleep(1)  # daemon time gap
        if dnsproxy.poll() is not None:  # unexpected exit
            logging.warning('dnsproxy unexpected exit')
            logging.debug('output of dnsproxy\n%s' % dnsproxy.stdout.read().decode('UTF-8'))
            dnsproxy = startDnsproxy(dnsCommand)


logging.warning('ProxyC starts running (%s)' % Version)

_thread.start_new_thread(startCompile, ('/usr', ))

_thread.start_new_thread(daemonDnsproxy, (['223.5.5.5', '119.28.28.28'], 53))

startServer(apiToken = 'dnomd343')
