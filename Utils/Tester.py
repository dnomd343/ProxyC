#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import requests
from threading import Thread
from Utils.Logger import logger
from Utils.Constant import WorkDir, TestHost, TestSite
from Utils.Common import md5Sum, genFlag, hostFormat, isVacantPort

Settings = {
    'workDir': WorkDir,
    'site': TestSite,
    'serverBind': '',
    'clientBind': '',
    'host': '',
    'cert': '',
    'key': '',
}


def loadBind(serverV6: bool = False, clientV6: bool = False) -> None:
    Settings['serverBind'] = '::1' if serverV6 else '127.0.0.1'
    Settings['clientBind'] = '::1' if clientV6 else '127.0.0.1'


def waitPort(port: int, times: int = 50, delay: int = 100) -> bool:  # wait until port occupied
    for i in range(times):
        if not isVacantPort(port):  # port occupied
            return True
        time.sleep(delay / 1000)  # default wait 100ms * 50 => 5s
    return False  # timeout


def genCert(host: str, certInfo: dict, remark: str = 'ProxyC') -> None:  # generate self-signed certificate
    certOrgInfo = ['--organization', remark, '--organizationUnit', remark]  # organization info
    logger.critical('Load self-signed certificate')
    os.system('mkdir -p %s' % Settings['workDir'])  # make sure that work directory exist

    # create CA data at first (by mad)
    logger.critical('Creating CA certificate and key...')
    os.system(' '.join(  # generate CA certificate and privkey
        ['mad', 'ca', '--ca', certInfo['caCert'], '--key', certInfo['caKey'], '--commonName', remark] + certOrgInfo
    ))

    # generate private key and sign certificate
    logger.critical('Signing certificate...')
    os.system(' '.join(['mad', 'cert', '--domain', host] + [  # generate certificate and privkey, then signed by CA
        '--ca', certInfo['caCert'], '--ca_key', certInfo['caKey'],
        '--cert', certInfo['cert'], '--key', certInfo['key'],
    ] + certOrgInfo))

    # install CA certificate and record self-signed cert info
    logger.critical('Installing CA certificate...')
    os.system('cat %s >> /etc/ssl/certs/ca-certificates.crt' % certInfo['caCert'])  # add into system's trust list


def loadCert(host: str = TestHost, certId: str = '') -> None:  # load certificate
    newCert = (certId == '')
    certId = genFlag(length = 8) if certId == '' else certId
    certInfo = {
        'caCert': os.path.join(Settings['workDir'], 'proxyc_%s_ca.pem' % certId),
        'caKey': os.path.join(Settings['workDir'], 'proxyc_%s_ca_key.pem' % certId),
        'cert': os.path.join(Settings['workDir'], 'proxyc_%s_cert.pem' % certId),
        'key': os.path.join(Settings['workDir'], 'proxyc_%s_cert_key.pem' % certId),
    }
    if newCert:
        genCert(host, certInfo)  # generate new certificate
    Settings['host'] = host
    Settings['cert'] = certInfo['cert']
    Settings['key'] = certInfo['key']
    logger.warning('Certificate load complete -> ID = %s' % certId)


def httpCheck(socksInfo: dict, url: str, testId: str, timeout: int = 10) -> None:
    socksProxy = 'socks5://%s:%i' % (hostFormat(socksInfo['addr'], v6Bracket = True), socksInfo['port'])
    try:
        logger.debug('[%s] Http request via %s' % (testId, socksProxy))
        request = requests.get(url, timeout = timeout, proxies = {  # http request via socks5
            'http': socksProxy,
            'https': socksProxy,
        })
        request.raise_for_status()  # throw error when server return 4xx or 5xx (don't actually need)
        logger.info('[%s] %s -> ok' % (testId, socksProxy))
    except Exception as exp:
        logger.error('[%s] %s -> error\n%s' % (testId, socksProxy, exp))  # show detail of error reason
        raise RuntimeError('Http request via socks5 failed')


def runTest(testInfo: dict, testUrl: str, testSelect: set or None, delay: int = 1) -> None:
    testId = md5Sum(testInfo['caption'])[:12]  # generate test ID
    if testSelect is not None:  # testSelect is None -> run all test
        if testId not in testSelect:  # skip unselected task
            return
    logger.warning('[%s] %s' % (testId, testInfo['caption']))  # show caption
    logger.debug('[%s] Server ID -> %s | Client ID -> %s' % (
        testId, testInfo['server'].id, testInfo['client'].id
    ))
    testInfo['server'].id = testId + '-server'
    testInfo['client'].id = testId + '-client'

    # build server and client and wait them start
    testInfo['server'].start()  # start test server
    if waitPort(testInfo['interface']['port']):  # wait for server
        logger.debug('[%s] Test server start complete' % testId)
    testInfo['client'].start()  # start test client
    if waitPort(testInfo['socks']['port']):  # wait for client
        logger.debug('[%s] Test client start complete' % testId)

    # start test process
    try:
        logger.debug('[%s] Test process start' % testId)
        time.sleep(delay)  # delay a short time before check
        httpCheck(testInfo['socks'], testUrl, testId)  # run http request test
        testInfo['client'].quit()  # clean up client
        testInfo['server'].quit()  # clean up server
    except:
        testInfo['client'].quit()
        testInfo['server'].quit()
        logger.warning('[%s] Client info' % testId)
        logger.error('[%(id)s-server]\n⬤ CMD => %(cmd)s\n⬤ ENV => %(env)s\n⬤ FILE => %(file)s\n%(output)s' % {
            'id': testId,
            'cmd': testInfo['client'].cmd,
            'env': testInfo['client'].env,
            'file': testInfo['client'].file,
            'output': '-' * 96 + '\n' + testInfo['client'].output + '-' * 96,
        })
        logger.warning('[%s] Server info' % testId)
        logger.error('[%(id)s-client]\n⬤ CMD => %(cmd)s\n⬤ ENV => %(env)s\n⬤ FILE => %(file)s\n%(output)s' % {
            'id': testId,
            'cmd': testInfo['server'].cmd,
            'env': testInfo['server'].env,
            'file': testInfo['server'].file,
            'output': '-' * 96 + '\n' + testInfo['server'].output + '-' * 96,
        })


def Test(testIter: iter, threadNum: int, testUrl: str, testFilter: set or None = None) -> None:
    threads = []
    while True:  # infinite loop
        try:
            for thread in threads:
                if thread.is_alive():  # skip running thread
                    continue
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
