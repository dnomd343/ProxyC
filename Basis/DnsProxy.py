#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import subprocess
from Basis.Logger import logging


def run(command: list) -> subprocess.Popen:
    logging.debug('Start dnsproxy -> %s' % command)
    return subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)


def daemon(process: subprocess.Popen, command: list, gap: int = 2) -> None:  # daemon dnsproxy process
    while True:  # start daemon
        time.sleep(gap)  # check time gap
        if process.poll() is not None:  # unexpected exit
            logging.error('DnsProxy unexpected exit\n%s\n%s%s' % (
                '-' * 96, process.stdout.read().decode('utf-8'), '-' * 96)
            )
            process = run(command)


def start(servers: list or None, port: int = 53, cache: int = 4194304) -> None:  # default cache size -> 4MiB
    if servers is not None and type(servers) != list:  # invalid server content
        logging.error('Invalid DNS server -> %s' % servers)
        return
    if servers is None or len(servers) == 0:  # use origin dns server
        logging.info('Skip dnsproxy process')
        return
    with open('/etc/resolv.conf', 'w') as dnsConfig:
        dnsConfig.write('nameserver 127.0.0.1\n')  # system dns settings
    dnsCommand = [
        'dnsproxy', '--all-servers',
        '--port', str(port),
        '--cache', '--cache-size', str(cache)
    ]
    for server in servers:
        dnsCommand += ['--upstream', server]  # upstream dns servers
    logging.warning('Start dnsproxy at port %i -> %s' % (port, servers))
    daemon(run(dnsCommand), dnsCommand)
