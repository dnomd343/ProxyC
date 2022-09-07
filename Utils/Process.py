#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import copy
import time
import ctypes
import signal
from Utils.Logger import logger
from Utils.Common import genFlag
from Utils.Exception import processException
from subprocess import Popen, STDOUT, DEVNULL

libcSysPaths = [
    '/usr/lib/libc.so.6',  # CentOS
    '/usr/lib64/libc.so.6',
    '/lib/libc.musl-i386.so.1',  # Alpine
    '/lib/libc.musl-x86_64.so.1',
    '/lib/libc.musl-aarch64.so.1',
    '/lib/i386-linux-gnu/libc.so.6',  # Debian / Ubuntu
    '/lib/x86_64-linux-gnu/libc.so.6',
    '/lib/aarch64-linux-gnu/libc.so.6',
]

libcPath = None
for path in libcSysPaths:
    if os.path.exists(path):  # try to locate libc.so
        libcPath = path
        break
if libcPath is None:  # lost libc.so -> unable to utilize prctl
    logger.warning('libc.so not found')
else:
    logger.info('libc.so -> %s' % libcPath)


class Process(object):
    """ Manage a sub process and it's configure file.

    Arguments:
      cmd: Command list, which use to start the program.

      env: Environment variables for sub process.

      file: dict or list or None, include path and content option.

      workDir: A directory for storing log files and configuration files.

      taskId: Task ID, defaults to 12 random characters length.

      isStart: Start the process after class init complete.

    Attributes:
        id, cmd, env, file, workDir, output
    """
    output = None  # sub process output if capture is True
    __capture = None  # capture the sub process output or not
    __logfile = None  # the log file which sub process output into STDOUT and STDERR
    __process = None  # CompletedProcess object of subprocess module

    @staticmethod
    def __preExec() -> None:
        ctypes.CDLL(libcPath).prctl(1, signal.SIGTERM)  # sub process killed when father process exit
        os.setpgrp()  # new process group

    def __checkWorkDir(self) -> None:  # check if the working directory is normal
        if os.path.isdir(self.workDir):
            return
        logger.warning('[%s] Work directory %s not exist' % (self.id, self.workDir))
        try:
            os.makedirs(self.workDir)  # just like `mkdir -p ...`
            logger.info('[%s] New directory -> %s' % (self.id, self.workDir))
        except:
            if os.path.exists(self.workDir):
                logger.error('[%s] %s already exist but not folder' % (self.id, self.workDir))
            else:
                logger.error('[%s] Unable to create new folder -> %s' % (self.id, self.workDir))
            raise processException('Working directory error')  # fatal error

    def __killProcess(self, killSignal: int) -> None:
        try:
            pgid = os.getpgid(self.__process.pid)  # progress group id
            os.killpg(pgid, killSignal)  # kill sub process group
            logger.debug('[%s] Send signal %i to PGID %i' % (self.id, killSignal, pgid))
        except:
            logger.warning('[%s] Failed to get PGID of sub process (PID = %i)' % (self.id, self.__process.pid))

    def __deleteFile(self, filePath: str) -> None:
        if not os.path.isfile(filePath):  # file not found (or not a file)
            logger.warning('[%s] File %s not found' % (self.id, filePath))
            return
        try:
            os.remove(filePath)  # remove config file
            logger.debug('[%s] File %s deleted successfully' % (self.id, filePath))
        except:
            logger.error('[%s] Unable to delete file %s' % (self.id, filePath))

    def __init__(self, workDir: str, taskId: str = '', isStart: bool = True,
                 cmd: str or list or None = None, env: dict or None = None, file: dict or list or None = None) -> None:
        self.id = genFlag(length = 12) if taskId == '' else taskId
        self.workDir = workDir
        self.env = copy.copy(env)  # depth = 1
        self.cmd = copy.copy([cmd] if type(cmd) == str else cmd)  # depth = 1
        self.file = copy.deepcopy([file] if type(file) == dict else file)  # depth = 2
        self.__checkWorkDir()  # ensure the working direction is normal
        logger.debug('[%s] Process command -> %s (%s)' % (self.id, self.cmd, self.env))
        if self.file is not None:
            if len(self.file) > 1:
                logger.debug('[%s] Manage %i files' % (self.id, len(self.file)))
            for file in self.file:  # traverse all files
                if not isStart:  # don't print log twice
                    logger.debug('[%s] File %s -> %s' % (self.id, file['path'], file['content']))
        if isStart:
            self.start()

    def setCmd(self, cmd: str or list) -> None:
        self.cmd = copy.copy([cmd] if type(cmd) == str else cmd)
        logger.info('[%s] Process setting command -> %s' % (self.id, self.cmd))

    def setEnv(self, env: dict or None) -> None:
        self.env = copy.copy(env)
        logger.info('[%s] Process setting environ -> %s' % (self.id, self.env))

    def setFile(self, file: dict or list or None) -> None:
        self.file = copy.deepcopy([file] if type(file) == dict else file)
        if self.file is None:
            logger.info('[%s] Process setting file -> None' % self.id)
            return
        for file in self.file:  # traverse all files
            logger.info('[%s] Process setting file %s -> %s' % (self.id, file['path'], file['content']))

    def start(self, isCapture: bool = True) -> None:
        self.__capture = isCapture
        logger.debug('[%s] Process ready to start (%s output capture)' % (
            self.id, 'with' if self.__capture else 'without'
        ))
        if self.cmd is None:  # ERROR CASE
            logger.error('[%s] Process miss start command' % self.id)
            raise processException('Miss start command')
        if self.__process is not None and self.__process.poll() is None:  # ERROR CASE
            logger.error('[%s] Process try to start but it is running' % self.id)
            raise processException('Process is still running')
        if self.env is not None and 'PATH' not in self.env and '/' not in self.cmd[0]:  # WARNING CASE
            logger.warning('[%s] Executable file in relative path but miss PATH in environ' % self.id)
        if self.file is not None:  # create and write file contents
            for file in self.file:
                with open(file['path'], 'w', encoding = 'utf-8') as fileObject: # save file content
                    fileObject.write(file['content'])
                    logger.debug('[%s] File %s -> %s' % (self.id, file['path'], file['content']))
        if self.__capture:  # with output capture
            self.__logfile = os.path.join(self.workDir, '%s.log' % self.id)
            logger.debug('[%s] Process output capture -> %s' % (self.id, self.__logfile))
            stdout = open(self.__logfile, 'w', encoding = 'utf-8')
            stderr = STDOUT  # combine the stderr with stdout
        else:  # discard all the output of sub process
            stdout = DEVNULL
            stderr = DEVNULL
        try:
            self.__process = Popen(
                self.cmd, env = self.env,
                stdout = stdout, stderr = stderr,
                preexec_fn = None if libcPath is None else Process.__preExec
            )
        except Exception as exp:
            logger.error('[%s] Process unable to start -> %s' % (self.id, exp))
            raise processException('Unable to start process')
        logger.info('[%s] Process running -> PID = %i' % (self.id, self.__process.pid))

    def signal(self, signalNum: int) -> None:  # send specified signal to sub process
        try:
            signalName = signal.Signals(signalNum).name
        except:
            signalName = 'unknown'
        logger.info('[%s] Send signal -> %i (%s)' % (self.id, signalNum, signalName))
        self.__process.send_signal(signalNum)

    def status(self) -> bool:  # check if the sub process is still running
        status = self.__process.poll() is None
        logger.debug('[%s] Process check status -> %s' % (self.id, 'running' if status else 'exit'))
        return status

    def wait(self, timeout: int or None = None) -> None:  # blocking wait sub process
        logger.info('[%s] Process wait -> timeout = %s' % (self.id, str(timeout)))
        try:
            self.__process.wait(timeout = timeout)
            logger.info('[%s] Process wait timeout -> exit' % self.id)
        except:
            logger.info('[%s] Process wait timeout -> running' % self.id)

    def quit(self, isForce: bool = False, waitTime: int = 50) -> None:  # wait 50ms in default
        killSignal = signal.SIGKILL if isForce else signal.SIGTERM  # 9 -> force kill / 15 -> terminate signal
        logger.debug('[%s] Kill signal -> %i (%s)' % (self.id, killSignal, signal.Signals(killSignal).name))
        self.__killProcess(killSignal)
        time.sleep(waitTime / 1000)  # sleep (ms -> s)
        while self.__process.poll() is None:  # confirm sub process exit
            self.__killProcess(killSignal)
            time.sleep(waitTime / 1000)
        logger.info('[%s] Process terminated -> PID = %i' % (self.id, self.__process.pid))
        if self.__capture:
            try:
                with open(self.__logfile, 'r', encoding = 'utf-8') as fileObject:  # read sub process output
                    self.output = fileObject.read()
                logger.debug('[%s] Process output capture -> length = %s' % (self.id, len(self.output)))
                self.__deleteFile(self.__logfile)
            except:
                logger.error('[%s] Failed to read capture file -> %s' % (self.id, self.__logfile))
        if self.file is not None:  # with config file
            for file in self.file:
                self.__deleteFile(file['path'])
