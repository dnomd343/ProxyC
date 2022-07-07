#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import copy

from Builder import Shadowsocks
from Builder import ShadowsocksR

from Basis.Logger import logging
from Basis.Process import Process
from Basis.Functions import genFlag, getAvailablePort


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
        loadFunction = {
            'ss': Shadowsocks.load,
            'ssr': ShadowsocksR.load,
        }
        if self.proxyType not in loadFunction:
            raise RuntimeError('Unknown proxy type')
        logging.info('[%s] Load %s proxy client at %s -> %s' % (self.id, self.proxyType, (
            (('[%s]' if ':' in self.socksAddr else '%s') + ':%i') % (self.socksAddr, self.socksPort)
        ), str(self.proxyInfo)))
        configFile = os.path.join(self.__workDir, self.id + '.json')
        command, fileContent, envVar = loadFunction[self.proxyType](self.proxyInfo, {
            'addr': self.socksAddr,
            'port': self.socksPort,
        }, configFile)
        envVar['PATH'] = '/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin'
        fileObject = {
            'path': configFile,
            'content': fileContent
        }
        self.__process = Process(self.__workDir, taskId = self.id, cmd = command, env = envVar, file = fileObject)

    def __init__(self, proxyType: str, proxyInfo: dict, taskId: str = '',
                 bind: str = '127.0.0.1', workDir: str = '/tmp/ProxyC') -> None:
        self.id = genFlag(length = 12) if taskId == '' else taskId
        self.__workDir = workDir
        self.proxyType = proxyType
        self.proxyInfo = copy.copy(proxyInfo)
        self.socksAddr = bind
        self.socksPort = getAvailablePort()
        self.__loadClient()

    def status(self) -> bool:
        return self.__process.status()

    def destroy(self) -> None:
        self.__process.quit()
        self.output = self.__process.output
