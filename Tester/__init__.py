#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import requests
from threading import Thread
from Basis.Logger import logging
from Tester.Settings import Settings
from Basis.Functions import md5Sum, genFlag, hostFormat, checkPortStatus

from Tester import Brook
from Tester import VMess
from Tester import VLESS
from Tester import Trojan
from Tester import TrojanGo
from Tester import Hysteria
from Tester import Shadowsocks
from Tester import ShadowsocksR

entry = {
    'ss': Shadowsocks.load(),
    'ss-all': Shadowsocks.load(isExtra = True),
    'ssr': ShadowsocksR.load(),
    'vmess': VMess.load(),
    'vless': VLESS.load(),
    'trojan': Trojan.load(),
    'trojan-go': TrojanGo.load(),
    'brook': Brook.load(),
    'hysteria': Hysteria.load(),
}


def waitPort(port: int, times: int = 100, delay: int = 100) -> bool:  # wait until port occupied
    for i in range(times):
        if not checkPortStatus(port):  # port occupied
            return True
        time.sleep(delay / 1000)  # default wait 100ms
    return False  # timeout


def httpCheck(socksInfo: dict, url: str, timeout: int = 10):
    socksProxy = 'socks5://%s:%i' % (hostFormat(socksInfo['addr'], v6Bracket = True), socksInfo['port'])
    try:
        proxy = {
            'http': socksProxy,
            'https': socksProxy,
        }
        request = requests.get(url, timeout = timeout, proxies = proxy)
        request.raise_for_status()
        logging.info('%s -> ok' % socksProxy)
    except Exception as exp:
        logging.error('%s -> error' % socksProxy)
        logging.error('requests exception\n' + str(exp))
        raise RuntimeError('socks5 test failed')


def runTest(testInfo: dict, testUrl: str, testFilter: set or None, delay: int = 1) -> None:
    testInfo['hash'] = md5Sum(testInfo['caption'])[:12]
    if testFilter is not None and testInfo['hash'] not in testFilter: return
    logging.warning('[%s] %s' % (testInfo['hash'], testInfo['caption']))
    testInfo['server'].start()  # start test server
    if waitPort(testInfo['interface']['port']):  # wait for server
        logging.debug('server start complete')
    testInfo['client'].start()  # start test client
    if waitPort(testInfo['socks']['port']):  # wait for client
        logging.debug('client start complete')
    try:
        logging.debug('start test process')
        time.sleep(delay)
        httpCheck(testInfo['socks'], testUrl)
        testInfo['client'].quit()
        testInfo['server'].quit()
    except:
        # client debug info
        testInfo['client'].quit()
        logging.warning('client info')
        logging.error('command -> %s' % testInfo['client'].cmd)
        logging.error('envVar -> %s' % testInfo['client'].env)
        logging.error('file -> %s' % testInfo['client'].file)
        logging.warning('client capture output')
        logging.error('\n%s' % testInfo['client'].output)
        # server debug info
        testInfo['server'].quit()
        logging.warning('server info')
        logging.error('command -> %s' % testInfo['server'].cmd)
        logging.error('envVar -> %s' % testInfo['server'].env)
        logging.error('file -> %s' % testInfo['server'].file)
        logging.warning('server capture output')
        logging.error('\n%s' % testInfo['server'].output)


def test(testIter: iter, threadNum: int, testUrl: str, testFilter: set or None = None):
    threads = []
    while True:  # infinite loop
        try:
            for thread in threads:
                if thread.is_alive(): continue
                threads.remove(thread)  # remove dead thread
            if len(threads) < threadNum:
                for i in range(threadNum - len(threads)):  # start threads within limit
                    thread = Thread(  # create new thread
                        target = runTest,
                        args = (next(testIter), testUrl, testFilter)
                    )
                    thread.start()
                    threads.append(thread)  # record thread info
            time.sleep(0.1)
        except StopIteration:  # traverse completed
            break
    for thread in threads:  # wait until all threads exit
        thread.join()


def loadCert(host: str = 'proxyc.net', remark: str = 'ProxyC'):
    loadPath = lambda x: os.path.join(Settings['workDir'], x)
    certFlag = genFlag(length = 8)
    caCert = loadPath('proxyc_%s_ca.pem' % certFlag)
    caKey = loadPath('proxyc_%s_ca_key.pem' % certFlag)
    cert = loadPath('proxyc_%s_cert.pem' % certFlag)
    key = loadPath('proxyc_%s_cert_key.pem' % certFlag)
    logging.critical('Create self-signed certificate')
    os.system('mkdir -p %s' % Settings['workDir'])  # create work directory
    logging.critical('Create CA certificate and key')
    os.system(' '.join(['mad', 'ca'] + [
        '--ca', caCert, '--key', caKey,
        '--commonName', remark,
        '--organization', remark,
        '--organizationUnit', remark,
    ]))
    logging.critical('Signing certificate')
    os.system(' '.join(['mad', 'cert'] + [
        '--ca', caCert, '--ca_key', caKey,
        '--cert', cert, '--key', key,
        '--domain', host,
        '--organization', remark,
        '--organizationUnit', remark,
    ]))
    logging.critical('Install CA certificate')
    os.system('cat %s >> /etc/ssl/certs/ca-certificates.crt' % caCert)
    Settings['host'] = host
    Settings['cert'] = cert
    Settings['key'] = key
    logging.warning('Certificate loading complete')
