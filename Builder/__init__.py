#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import copy

from Builder import Shadowsocks

from Basis.Logger import logging
from Basis.Process import Process
from Basis.Functions import genFlag, getAvailablePort

default = {
    'workDir': '/tmp/ProxyC',
    'bindAddr': '127.0.0.1',
    'binDir': '/usr/bin',
}


class Builder(object):
    """ Build the proxy client process and expose socks5 port.

    Arguments:
      proxy: Proxy node information.

      bind: Socks5 proxy bind address.

      workDir: A directory for storing configuration files.

      taskId: Task ID, defaults to 12 random characters length.

      isStart: Start the process after class init complete.

    Attributes:
        id, proxyType, proxyInfo, socksAddr, socksPort, output
    """
    output = None

    def __loadClient(self, isStart: bool):
        loadFunction = {
            'ss': Shadowsocks.load,
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
        envVar['PATH'] = default['binDir']
        fileObject = {
            'path': configFile,
            'content': fileContent
        }
        self.__process = Process(self.__workDir, taskId = self.id,
                                 isStart = isStart, cmd = command, env = envVar, file = fileObject)

    def __init__(self, proxy: dict, taskId: str = '', isStart: bool = True,
                 bind: str = default['bindAddr'], workDir: str = default['workDir']) -> None:
        self.id = genFlag(length = 12) if taskId == '' else taskId
        self.__workDir = workDir
        self.proxyType = proxy['type']
        self.proxyInfo = copy.copy(proxy['info'])
        self.socksAddr = bind
        self.socksPort = getAvailablePort()
        self.__loadClient(isStart)

    def status(self) -> bool:
        return self.__process.status()

    def destroy(self) -> None:
        self.__process.quit()
        self.output = self.__process.output
