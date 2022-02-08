#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import time
import ctypes
import random
import socket
import subprocess

from ProxyBuilder import Shadowsocks
from ProxyBuilder import ShadowsocksR

libcPaths = [
    '/usr/lib64/libc.so.6', # CentOS
    '/lib/i386-linux-gnu/libc.so.6', # Debian / Ubuntu
    '/lib/x86_64-linux-gnu/libc.so.6',
    '/lib/aarch64-linux-gnu/libc.so.6',
    '/lib/libc.musl-x86_64.so.1', # Alpine
]

def __checkPortAvailable(port): # 检测端口可用性
    try:
        ipv4_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ipv4_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ipv4_tcp.bind(('0.0.0.0', port))
        ipv4_udp.bind(('0.0.0.0', port))
        ipv4_tcp.close()
        ipv4_udp.close()
        ipv6_tcp = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        ipv6_udp = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        ipv6_tcp.bind(('::', port))
        ipv6_udp.bind(('::', port))
        ipv6_tcp.close()
        ipv6_udp.close()
        return True # IPv4 TCP / IPv4 UDP / IPv6 TCP / IPv6 UDP 均无占用
    except:
        return False
    finally:
        try: # 关闭socket
            if ipv4_tcp: ipv4_tcp.close()
            if ipv4_udp: ipv4_udp.close()
            if ipv6_tcp: ipv6_tcp.close()
            if ipv6_udp: ipv6_udp.close()
        except: pass

def __genTaskFlag(length = 16): # 生成任务代号
    flag = ""
    for i in range(0, length):
        tmp = random.randint(0, 15)
        if tmp >= 10:
            flag += chr(tmp + 87) # a ~ f
        else:
            flag += str(tmp) # 0 ~ 9
    return flag

def __getAvailablePort(rangeStart, rangeEnd): # 获取一个空闲端口
    if rangeStart > rangeEnd:
        return None
    while True:
        port = random.randint(rangeStart, rangeEnd) # 随机选取
        if __checkPortAvailable(port):
            return port
        time.sleep(0.1) # 100ms

def build(proxyInfo, configDir): # 构建代理节点连接
    taskFlag = __genTaskFlag()
    socksPort = __getAvailablePort(1024, 65535) # Socks5测试端口
    if not 'type' in proxyInfo:
        return None
    proxyType = proxyInfo['type'] # 节点类型
    proxyInfo.pop('type')

    configFile = configDir + '/' + taskFlag + '.json' # 配置文件路径
    if proxyType == 'ss': # Shadowsocks节点
        startCommand, fileContent = Shadowsocks.load(proxyInfo, socksPort, configFile)
    elif proxyType == 'ssr': # ShadowsocksR节点
        startCommand, fileContent = ShadowsocksR.load(proxyInfo, socksPort, configFile)
    else: # 未知类型
        return None
    if startCommand == None: # 格式出错
        return None
    try:
        with open(configFile, 'w') as fileObject:
            fileObject.write(fileContent) # 保存配置文件
    except:
        print("Unable write to file " + configFile)
        return None # 配置文件写入失败

    try:
        for libcPath in libcPaths:
            if os.path.exists(libcPath): # 定位libc.so文件
                break
        exitWithMe = lambda: ctypes.CDLL(libcPath).prctl(1, 15) # SIGTERM
        process = subprocess.Popen(startCommand,
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL,
            preexec_fn = exitWithMe) # 子进程跟随退出
    except:
        process = subprocess.Popen(startCommand,
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL) # prctl失败 回退正常启动

    return { # 返回连接参数
        'flag': taskFlag,
        'port': socksPort,
        'file': configFile,
        'process': process,
        'pid': process.pid,
    }

def check(taskInfo): # 检查客户端是否正常
    if taskInfo == None:
        return False
    process = taskInfo['process']
    if process.poll() != None:
        return False # 死亡
    else:
        return True # 正常

def destroy(taskInfo): # 结束客户端并清理
    if taskInfo == None:
        return
    process = taskInfo['process']
    if process.poll() == None: # 未死亡
        process.terminate() # SIGTERM
        while process.poll() == None: # 等待退出
            time.sleep(1)
            process.terminate()
    try:
        os.remove(taskInfo['file']) # 删除配置文件
    except: pass

def test():
    import requests
    import ProxyBuilder.test as tester

    data = tester.Shadowsocks.test(1080, 'dnomd343')

    for field in data:
        serverProcess = subprocess.Popen(
            field['serverCommand'],
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL)
        time.sleep(0.5) # 等待服务端启动完成
        if serverProcess.poll() != None: # 服务端启动失败
            print("server unexpected exit")
            continue
        print(field['caption'])

        client = build(field['proxyInfo'], '/tmp/ProxyC')
        time.sleep(0.5) # 等待客户端启动完成
        if not check(client):
            print("client unexpected exit") # 客户端启动失败
        else:
            try:
                startTime = time.time_ns()
                r = requests.get('http://gstatic.com/generate_204', proxies = {
                    'http': 'socks5://127.0.0.1:' + str(client['port']),
                    'https': 'socks5://127.0.0.1:' + str(client['port']),
                })
                if r.status_code == 204:
                    delay = (time.time_ns() - startTime) / (10 ** 6)
                    print(format(delay, '.2f') + 'ms')
                else:
                    print("connect error")
            except:
                print("request error")
            destroy(client) # 关闭客户端
            time.sleep(0.3)
        serverProcess.terminate() # 关闭服务端
        time.sleep(0.3)
        print()
