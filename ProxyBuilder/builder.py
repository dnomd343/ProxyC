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
    '/lib/libc.musl-x86_64.so.1', # Alpine
    '/lib/i386-linux-gnu/libc.so.6', # Debian / Ubuntu
    '/lib/x86_64-linux-gnu/libc.so.6',
    '/lib/aarch64-linux-gnu/libc.so.6',
]

def __checkPortAvailable(port: int) -> bool: # 检测端口可用性
    ipv4_tcp = None
    ipv4_udp = None
    ipv6_tcp = None
    ipv6_udp = None
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
    finally: # 关闭socket
        try:
            ipv4_tcp.close()
        except: pass
        try:
            ipv4_udp.close()
        except: pass
        try:
            ipv6_tcp.close()
        except: pass
        try:
            ipv6_udp.close()
        except: pass

def __genTaskFlag(length: int = 16) -> str: # 生成任务代号
    flag = ''
    for i in range(0, length):
        tmp = random.randint(0, 15)
        if tmp >= 10:
            flag += chr(tmp + 87) # a ~ f
        else:
            flag += str(tmp) # 0 ~ 9
    return flag

def __getAvailablePort(rangeStart: int, rangeEnd: int) -> int or None: # 获取一个空闲端口
    if rangeStart > rangeEnd or rangeStart < 0 or rangeEnd > 65535:
        return None
    while True:
        port = random.randint(rangeStart, rangeEnd) # 随机选取
        if __checkPortAvailable(port):
            return port
        time.sleep(0.1) # 100ms

def build(proxyInfo: dict, configDir: str,
          portRangeStart: int = 1024, portRangeEnd: int = 65535) -> tuple[bool or None, str or dict]:
    """
    创建代理节点客户端

        程序内部错误:
            return None, {reason}

        代理节点无效:
            return False, {reason}

        代理工作正常:
            return True, {
                'flag': taskFlag,
                'port': socksPort,
                'file': configFile,
                'process': process
            }
    """
    taskFlag = __genTaskFlag() # 生成测试标志
    socksPort = __getAvailablePort(portRangeStart, portRangeEnd) # 获取Socks5测试端口
    if 'type' not in proxyInfo: # 未指定节点类型
        return False, 'Proxy type not specified'
    if proxyInfo['type'] == 'ss': # Shadowsocks节点
        clientObj = Shadowsocks
    elif proxyInfo['type'] == 'ssr': # ShadowsocksR节点
        clientObj = ShadowsocksR
    else: # 未知类型
        return False, 'Unknown proxy type'

    configFile = configDir + '/' + taskFlag + '.json' # 配置文件路径
    startCommand, fileContent, envVar = clientObj.load(proxyInfo, socksPort, configFile) # 载入配置
    if startCommand is None: # 格式出错
        return False, 'Format error with ' + str(proxyInfo['type'])
    try:
        with open(configFile, 'w') as fileObject: # 保存配置文件
            fileObject.write(fileContent)
    except: # 配置文件写入失败
        return None, "Unable write to file " + str(configFile)

    process = None
    try: # 子进程形式启动
        for libcPath in libcPaths:
            if os.path.exists(libcPath): # 定位libc.so文件
                break
        process = subprocess.Popen( # 启动子进程
            startCommand,
            env = envVar,
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL,
            preexec_fn = lambda: ctypes.CDLL(libcPath).prctl(1, 15) # 子进程跟随退出
        )
    except:
        try:
            process = subprocess.Popen( # prctl失败 回退正常启动
                startCommand,
                env = envVar,
                stdout = subprocess.DEVNULL,
                stderr = subprocess.DEVNULL
            )
        except:
            pass
    if process is None: # 启动失败
        return None, 'Subprocess start failed by `' + ' '.join(startCommand) + '`'

    return True, { # 返回连接参数
        'flag': taskFlag,
        'port': socksPort,
        'file': configFile,
        'process': process
    }

def check(client: dict) -> bool or None:
    """
    检查客户端是否正常运行

        检测出错: return None

        工作异常: return False

        工作正常: return True
    """
    try:
        return client['process'].poll() is None
    except:
        return None # 异常

def destroy(client: dict) -> bool:
    """
    结束客户端并清理

        销毁异常: return False

        销毁成功: return True
    """
    try:
        process = client['process']
        if process.poll() is None: # 未死亡
            while process.poll() is None: # 等待退出
                process.terminate() # SIGTERM
                time.sleep(0.2)
    except:
        return False

    try:
        file = client['file']
        if os.path.exists(file) and os.path.isfile(file):
            os.remove(file) # 删除配置文件
            return True # 销毁成功
    except:
        pass
    return False
