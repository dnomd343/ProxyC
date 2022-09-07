#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import subprocess
from Utils.Logger import logger


def run(command: list) -> subprocess.Popen:
    logger.debug('Start dnsproxy -> %s' % command)
    return subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)  # stdout and stderr


def daemon(process: subprocess.Popen, command: list, gap: int = 3) -> None:  # daemon dnsproxy process
    while True:  # start daemon process
        time.sleep(gap)  # check time gap (default 3s)
        if process.poll() is not None:  # unexpected exit
            logger.error('DnsProxy unexpected exit\n%s\n%s%s' % (
                '-' * 96, process.stdout.read().decode(encoding = 'utf-8'), '-' * 96)
            )
            process = run(command)


def start(servers: str or list or None, port: int = 53, cache: int = 4194304) -> None:  # default cache size -> 4MiB
    servers = [servers] if type(servers) == str else servers
    if servers is not None and type(servers) != list:  # invalid server content
        logger.error('Invalid DNS server -> %s' % servers)
        return
    if servers is None or len(servers) == 0:  # use origin dns server
        logger.info('Skip dnsproxy process')
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
    logger.warning('Start dnsproxy at port %i -> %s' % (port, servers))
    daemon(run(dnsCommand), dnsCommand)
