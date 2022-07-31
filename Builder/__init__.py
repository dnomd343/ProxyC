#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import copy

from Builder import Brook
from Builder import VMess
from Builder import VLESS
from Builder import Trojan
from Builder import TrojanGo
from Builder import Shadowsocks
from Builder import ShadowsocksR

from Basis.Logger import logging
from Basis.Process import Process
from Basis.Functions import genFlag, getAvailablePort

pathEnv = '/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin'
clientEntry = {
    'ss': [Shadowsocks.load, '.json'],
    'ssr': [ShadowsocksR.load, '.json'],
    'vmess': [VMess.load, '.json'],
    'vless': [VLESS.load, '.json'],
    'trojan': [Trojan.load, '.json'],
    'trojan-go': [TrojanGo.load, '.json'],
    'brook': [Brook.load, ''],
}


class Builder(object):
    """ Build the proxy client process and expose socks5 port.

    Arguments:
      proxyType: Proxy node type.

      proxyInfo: Proxy node information.

      bind: Socks5 proxy bind address.

      workDir: A directory for storing configuration files.

      taskId: Task ID, defaults to 12 random characters length.

    Attributes:
        id, proxyType, proxyInfo, socksAddr, socksPort, output
    """
    output = None

    def __loadClient(self):
        logging.info('[%s] Load %s proxy client at %s -> %s' % (self.id, self.proxyType, (
            (('[%s]' if ':' in self.socksAddr else '%s') + ':%i') % (self.socksAddr, self.socksPort)
        ), str(self.proxyInfo)))
        configFile = os.path.join(  # config file path
            self.__workDir, self.id + clientEntry[self.proxyType][1]  # workDir + taskId + suffix
        )
        command, fileContent, envVar = clientEntry[self.proxyType][0](self.proxyInfo, {  # load client boot info
            'addr': self.socksAddr,
            'port': self.socksPort,
        }, configFile)
        fileObject = {  # add config file settings
            'path': configFile,
            'content': fileContent
        }
        envVar['PATH'] = pathEnv  # add PATH env (some programs need it)
        self.__process = Process(self.__workDir, taskId = self.id, cmd = command, env = envVar, file = fileObject)

    def __init__(self, proxyType: str, proxyInfo: dict, taskId: str = '',
                 bind: str = '127.0.0.1', workDir: str = '/tmp/ProxyC') -> None:  # init proxy client
        if proxyType not in clientEntry:
            raise RuntimeError('Unknown proxy type')
        self.id = genFlag(length = 12) if taskId == '' else taskId  # load task ID
        self.__workDir = workDir
        self.proxyType = proxyType  # proxy type -> ss / ssr / vmess ...
        self.proxyInfo = copy.copy(proxyInfo)  # proxy object -> contain connection info
        self.socksAddr = bind
        self.socksPort = getAvailablePort()  # random port for socks5 exposed
        self.__loadClient()

    def status(self) -> bool:  # check if the sub process is still running
        return self.__process.status()

    def destroy(self) -> None:  # kill sub process and remove config file
        self.__process.quit()
        self.output = self.__process.output
