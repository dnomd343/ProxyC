#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import sys
import time
import signal
import subprocess

import Check as Checker
import ProxyTester as Tester

testConfig = {
    'bind': '0.0.0.0',
    'addr': '172.17.0.2',
    'port': 12345,
    'passwd': 'dnomd343',
    'host': 'local.343.re',
    'path': '/test',
    'service': 'dnomd343',
    'file': '/tmp/proxycTest.json',
    'id': '1f7aa040-94d8-4b53-ae85-af6946d550bb',
    'cert': '/etc/ssl/certs/343.re/fullchain.pem',
    'key': '/etc/ssl/certs/343.re/privkey.pem',
}

def testBuild(config: dict): # load file and start process
    if config['filePath'] is not None:
        with open(config['filePath'], 'w') as fileObject:  # save file
            fileObject.write(config['fileContent'])
    if config['startCommand'] is None:
        return None
    return subprocess.Popen( # start process
        config['startCommand'],
        env = config['envVar'],
        stdout = subprocess.DEVNULL,
        stderr = subprocess.DEVNULL,
        preexec_fn = os.setpgrp # new process group
    )

def testDestroy(config: dict, process): # remove file and kill process
    if process is not None and process.poll() is None:  # still alive
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)  # kill process group
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
        print('\n--------------------------------------------------------------------------------------------------------------------------------')
        print(option)
        print('--------------------------------------------------------------------------------------------------------------------------------\n')
        testDestroy(option['server'], serverProcess)  # destroy and exit
        if option['aider'] is not None:
            testDestroy(option['aider'], aiderProcess)
        raise Exception('check error')
    delay = checkResult['check']['http']['delay'] # get http delay
    if delay > 0:
        print(format(delay, '.2f') + 'ms')
    else:
        print('ERROR')

    testDestroy(option['server'], serverProcess) # destroy server process
    if option['aider'] is not None:
        testDestroy(option['aider'], aiderProcess) # destroy aider process

if len(sys.argv) == 1: # no param
    print('Unknown test type')
    sys.exit(1)
testList = Tester.test(sys.argv[1].lower().strip(), testConfig) # get test list

if len(sys.argv) == 2: # test all
    for i in range(0, len(testList)):
        print(str(i), end = ': ')
        testObject(testList[i])
    sys.exit(0)

if len(sys.argv) == 3: # test target index
    testObject(testList[int(sys.argv[2])])
else:
    print('Too many options')
