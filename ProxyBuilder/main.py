#!/usr/bin/python
# -*- coding:utf-8 -*-

import os
import time
import ctypes
import random
import socket
import subprocess
from ProxyBuilder import Shadowsocks

libcPaths = [
    '/usr/lib64/libc.so.6', # CentOS
    '/lib/i386-linux-gnu/libc.so.6', # Debian / Ubuntu
    '/lib/x86_64-linux-gnu/libc.so.6',
    '/lib/aarch64-linux-gnu/libc.so.6',
    '/lib/libc.musl-x86_64.so.1', # Alpine
]

# TODO: TCP/UDP IPv4/IPv6
def __checkPortAvailable(port, host = '127.0.0.1'): # 检测端口可用性
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, int(port)))
        return False
    except socket.error:
        return True
    finally:
        if s:
            s.close()

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
    if (proxyType == 'shadowsocks'): # Shadowsocks节点
        startCommand = Shadowsocks.load(proxyInfo, socksPort, configFile)
    else: # 未知类型
        return None

    try:
        for libcPath in libcPaths:
            if os.path.exists(libcPath): # 定位libc.so文件
                break
        exitWithMe = lambda: ctypes.CDLL(libcPath).prctl(1, 15) # SIGTERM
        process = subprocess.Popen(startCommand, \
            stdout = subprocess.DEVNULL, \
            stderr = subprocess.DEVNULL, \
            preexec_fn = exitWithMe) # 子进程跟随退出
    except:
        process = subprocess.Popen(startCommand, \
            stdout = subprocess.DEVNULL, \
            stderr = subprocess.DEVNULL) # prctl失败 回退正常启动

    return { # 返回连接参数
        'flag': taskFlag,
        'port': socksPort,
        'file': configFile,
        'process': process,
        'pid': process.pid,
    }

def check(taskInfo): # 检查客户端是否正常
    process = taskInfo['process']
    if process.poll() != None:
        return False # 死亡
    else:
        return True # 正常

def destroy(taskInfo): # 结束客户端并清理
    process = taskInfo['process']
    if process.poll() == None: # 未死亡
        process.terminate() # SIGTERM
        while process.poll() == None: # 等待退出
            time.sleep(1)
            process.terminate()
    try:
        os.remove(taskInfo.file) # 删除配置文件
    except: pass
