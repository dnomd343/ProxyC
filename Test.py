#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import time
import subprocess

import Check as Checker
import ProxyTester as Tester

testConfig = {
    'port': 12345,
    'passwd': 'dnomd343',
    'host': 'dns.343.re',
    'cert': '/etc/ssl/certs/dns.343.re/certificate.crt',
    'key': '/etc/ssl/certs/dns.343.re/private.key'
}

def testBuild(config: dict): # load file and start process
    if config['filePath'] is not None:
        with open(config['filePath'], 'w') as fileObject:  # save file
            fileObject.write(config['fileContent'])
    return subprocess.Popen( # start process
        config['startCommand'],
        env = config['envVar'],
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL
    )

def testDestroy(config: dict, process): # remove file and kill process
    if process.poll() is None:  # still alive
        while process.poll() is None:  # wait for exit
            process.terminate()  # SIGTERM
            time.sleep(0.2)
    if config['filePath'] is not None:
        os.remove(config['filePath']) # remove file

def testObject(option: dict) -> None: # test target object
    aiderProcess = None
    serverProcess = testBuild(option['server']) # start server process
    if option['aider'] is not None:
        aiderProcess = testBuild(option['aider']) # start aider process

    checkResult = Checker.proxyTest({ # http check
        'check': ['http'],
        'info': option['proxy']
    })
    print(option['caption'], end=' -> ')
    if not checkResult['success']: # client build error
        print('\n----------------------------------------------------------------')
        print(option)
        print('----------------------------------------------------------------\n')
        raise Exception('check error')
    delay = checkResult['check']['http']['delay'] # get http delay
    print(str(delay) + 'ms')

    testDestroy(option['server'], serverProcess) # destroy server process
    if option['aider'] is not None:
        testDestroy(option['aider'], aiderProcess) # destroy aider process

if len(sys.argv) == 1: # no param
    print('Unknown test type')
    sys.exit(1)
testList = Tester.test(sys.argv[1], testConfig) # get test list

if len(sys.argv) == 2: # test all
    for i in range(0, len(testList)):
        print(str(i), end = ': ')
        testObject(testList[i])
    sys.exit(0)

if len(sys.argv) == 3: # test target index
    testObject(testList[int(sys.argv[2])])
else:
    print('Too many options')
