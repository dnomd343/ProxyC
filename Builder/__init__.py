#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import copy
from Filter import Filter
from Basis.Logger import logging
from Basis.Process import Process
from Basis.Functions import v6AddBracket
from Basis.Constant import WorkDir, PathEnv
from Basis.Functions import genFlag, getAvailablePort
from Basis.Exception import buildException, filterException

from Builder import Brook
from Builder import VMess
from Builder import VLESS
from Builder import Trojan
from Builder import TrojanGo
from Builder import Hysteria
from Builder import Shadowsocks
from Builder import ShadowsocksR

clientEntry = {
    'ss': [Shadowsocks.load, '.json'],
    'ssr': [ShadowsocksR.load, '.json'],
    'vmess': [VMess.load, '.json'],
    'vless': [VLESS.load, '.json'],
    'trojan': [Trojan.load, '.json'],
    'trojan-go': [TrojanGo.load, '.json'],
    'brook': [Brook.load, ''],
    'hysteria': [Hysteria.load, '.json'],
}


class Builder(object):
    """ Build the proxy client process and expose socks5 port.

    Arguments:
      proxyType: Proxy node type.

      proxyInfo: Proxy node information.

      bindAddr: Socks5 proxy bind address.

      taskId: Task ID, defaults to 12 random characters length.

    Attributes:
        id, proxyType, proxyInfo, socksAddr, socksPort, output
    """
    output = None  # output capture of proxy client (after process exit)

    def __loadClient(self):
        logging.info('[%s] Builder load %s client at %s -> %s' % (
            self.id, self.proxyType,
            'socks5://%s:%i' % (v6AddBracket(self.socksAddr), self.socksPort), self.proxyInfo
        ))
        configFile = os.path.join(  # config file path
            WorkDir, self.id + clientEntry[self.proxyType][1]  # workDir + taskId + file suffix
        )
        logging.debug('[%s] Builder config file -> %s' % (self.id, configFile))
        command, fileContent, envVar = clientEntry[self.proxyType][0](self.proxyInfo, {  # load client boot info
            'addr': self.socksAddr,  # specify socks5 info
            'port': self.socksPort,
        }, configFile)
        envVar['PATH'] = PathEnv  # add PATH env (some programs need it)
        self.__process = Process(WorkDir, taskId = self.id, cmd = command, env = envVar, file = {  # start process
            'path': configFile,
            'content': fileContent
        })

    def __init__(self, proxyType: str, proxyInfo: dict, bindAddr: str, taskId: str = '') -> None:  # init proxy client
        self.id = genFlag(length = 12) if taskId == '' else taskId  # load task ID
        if proxyType not in clientEntry:
            logging.error('[%s] Builder receive unknown proxy type %s' % (self.id, proxyType))
            raise buildException('Unknown proxy type')
        self.proxyType = proxyType  # proxy type -> ss / ssr / vmess ...
        self.proxyInfo = Filter(proxyType, proxyInfo)  # filter input proxy info
        self.proxyInfo = copy.copy(proxyInfo)  # connection info
        self.socksAddr = bindAddr
        self.socksPort = getAvailablePort()  # random port for socks5 exposed
        self.__loadClient()

    def status(self) -> bool:  # check if the sub process is still running
        return self.__process.status()

    def destroy(self) -> None:  # kill sub process and remove config file
        logging.debug('[%s] Builder destroy' % self.id)
        self.__process.quit()
        self.output = self.__process.output
