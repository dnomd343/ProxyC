#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import copy
import time
import ctypes
import signal
from Basis.Logger import logging
from Basis.Functions import genFlag
from subprocess import Popen, STDOUT, DEVNULL

libcPaths = [
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
for libc in libcPaths:
    if os.path.exists(libc):  # try to locate libc.so
        libcPath = libc
        break
if libcPath is None:  # lost libc.so -> unable to utilize prctl
    logging.warning('libc.so not found')
else:
    logging.info('libc.so -> ' + str(libcPath))


class Process(object):
    """ Manage a sub process and it's file.

    Arguments:
      cmd: Command list, which use to start the program.

      env: Environment variables for sub process.

      file: dict or list or None, include path and content option.

      workDir: A directory for storing log files and configuration files.

      taskId: Task id, defaults to 12 random characters length.

    Attributes:
        id, workDir, output
    """
    output = None  # sub process output if capture is True
    __capture = None  # capture the sub process output or not
    __logfile = None  # the log file which sub process output into STDOUT and STDERR
    __process = None  # CompletedProcess object of subprocess module

    @staticmethod
    def __preExec() -> None:
        # TODO: remember to remove test code
        print('WARNING: pre exec at static method')
        print('libc.so: ' + str(libcPath))
        ctypes.CDLL(libcPath).prctl(1, signal.SIGTERM)  # sub process killed when father process exit
        os.setpgrp()  # new process group

    def __checkWorkDir(self) -> None:  # check if the working directory is normal
        if os.path.isdir(self.workDir):
            return
        logging.warning('[%s] Work directory %s not exist' % (self.id, self.workDir))
        try:
            os.makedirs(self.workDir)  # just like `mkdir -p ...`
            logging.info('[%s] New directory -> %s' % (self.id, self.workDir))
        except:
            if os.path.exists(self.workDir):
                logging.error('[%s] %s already exist but not folder' % (self.id, self.workDir))
            else:
                logging.error('[%s] Unable to create new folder -> %s' % (self.id, self.workDir))
            raise RuntimeError('working directory error')  # fatal error

    def __killProcess(self, killSignal: int) -> None:
        try:
            pgid = os.getpgid(self.__process.pid)  # progress group id
            os.killpg(pgid, killSignal)  # kill sub process group
            logging.debug('[%s] Send kill signal to PGID %i' % (self.id, pgid))
        except:
            logging.warning('[%s] Failed to get PGID of sub process (PID = %i)' % (self.id, self.__process.pid))

    def __deleteFile(self, filePath: str) -> None:
        if not os.path.isfile(filePath):  # file not found (or not a file)
            logging.warning('[%s] File %s not found' % (self.id, filePath))
            return
        try:
            os.remove(filePath)  # remove config file
            logging.debug('[%s] File %s deleted successfully' % (self.id, filePath))
        except:
            logging.error('[%s] Unable to delete file %s' % (self.id, filePath))

    def __init__(self, workDir: str, taskId: str = '', isStart: bool = True,
                 cmd: str or list or None = None, env: dict or None = None, file: dict or list or None = None) -> None:
        self.id = genFlag(length = 12) if taskId == '' else taskId
        self.workDir = workDir
        self.__env = copy.copy(env)  # depth = 1
        self.__cmd = copy.copy([cmd] if type(cmd) == str else cmd)  # depth = 1
        self.__file = copy.deepcopy([file] if type(file) == dict else file)  # depth = 2
        self.__checkWorkDir()  # ensure the working direction is normal
        logging.debug('[%s] Process command -> %s (%s)' % (self.id, self.__cmd, self.__env))
        if self.__file is not None:
            if len(self.__file) > 1:
                logging.debug('[%s] Manage %i files' % (self.id, len(self.__file)))
            for file in self.__file:  # traverse all files
                if not isStart:  # don't print log twice
                    logging.debug('[%s] File %s -> %s' % (self.id, file['path'], file['content']))
        if isStart:
            self.start()

    def setCmd(self, cmd: str or list) -> None:
        self.__cmd = copy.copy([cmd] if type(cmd) == str else cmd)
        logging.info('[%s] Process setting command -> %s' % (self.id, self.__cmd))

    def setEnv(self, env: dict or None) -> None:
        self.__env = copy.copy(env)
        logging.info('[%s] Process setting environ -> %s' % (self.id, self.__env))

    def setFile(self, file: dict or list or None) -> None:
        self.__file = copy.deepcopy([file] if type(file) == dict else file)
        if self.__file is None:
            logging.info('[%s] Process setting file -> None' % self.id)
            return
        for file in self.__file:  # traverse all files
            logging.info('[%s] Process setting file %s -> %s' % (self.id, file['path'], file['content']))

    def start(self, isCapture: bool = True) -> None:
        self.__capture = isCapture
        logging.debug('[%s] Process ready to start (%s)' % (self.id, (
            'with output capture' if self.__capture else 'without output capture'
        )))
        if self.__cmd is None:  # ERROR CASE
            logging.error('[%s] Process miss start command' % self.id)
            raise RuntimeError('miss start command')
        if self.__process is not None and self.__process.poll() is None:  # ERROR CASE
            logging.error('[%s] Sub process is still running' % self.id)
            raise RuntimeError('sub process is still running')
        if self.__env is not None and 'PATH' not in self.__env and '/' not in self.__cmd[0]:  # WARNING CASE
            logging.warning('[%s] Executable file in relative path but miss PATH in environ' % self.id)
        if self.__file is not None:  # create and write file contents
            for file in self.__file:
                with open(file['path'], 'w', encoding = 'utf-8') as fileObject: # save file content
                    fileObject.write(file['content'])
                    logging.debug('[%s] File %s -> %s' % (self.id, file['path'], file['content']))
        if self.__capture:  # with output capture
            self.__logfile = os.path.join(self.workDir, self.id + '.log')
            logging.debug('[%s] Output capture file -> %s' % (self.id, self.__logfile))
            stdout = open(self.__logfile, 'w', encoding = 'utf-8')
            stderr = STDOUT  # combine the stderr with stdout
        else:  # discard all the output of sub process
            stdout = DEVNULL
            stderr = DEVNULL
        self.__process = Popen(self.__cmd, env = self.__env, stdout = stdout,
                             stderr = stderr, preexec_fn = None if libcPath is None else Process.__preExec)
        logging.info('[%s] Process running -> PID = %i' % (self.id, self.__process.pid))

    def signal(self, signalNum: int) -> None:  # send specified signal to sub process
        try:
            signalName = signal.Signals(signalNum).name
        except:
            signalName = 'unknown'
        logging.info('[%s] Send signal -> %i (%s)' % (self.id, signalNum, signalName))
        self.__process.send_signal(signalNum)

    def status(self) -> bool:  # check if the sub process is still running
        status = self.__process.poll() is None
        logging.debug('[%s] Check status -> %s' % (self.id, 'running' if status else 'exit'))
        return status

    def wait(self, timeout: int or None = None) -> None:  # blocking wait sub process
        logging.info('[%s] Process wait -> timeout = %s' % (self.id, str(timeout)))
        try:
            self.__process.wait(timeout = timeout)
            logging.info('[%s] Process wait timeout -> sub process exit' % self.id)
        except:
            logging.info('[%s] Process wait timeout -> sub process still running' % self.id)

    def quit(self, isForce: bool = False, waitTime: int = 50) -> None:  # wait 50ms in default
        killSignal = signal.SIGKILL if isForce else signal.SIGTERM  # 9 -> force kill / 15 -> terminate signal
        logging.debug('[%s] Kill signal = %i (%s)' % (self.id, killSignal, signal.Signals(killSignal).name))
        self.__killProcess(killSignal)
        time.sleep(waitTime / 1000)  # sleep (ms -> s)
        while self.__process.poll() is None:  # confirm sub process exit
            self.__killProcess(killSignal)
            time.sleep(waitTime / 1000)
        logging.info('[%s] Process terminated -> PID = %i' % (self.id, self.__process.pid))
        if self.__capture:
            try:
                with open(self.__logfile, 'r', encoding = 'utf-8') as fileObject:  # read sub process output
                    self.output = fileObject.read()
                logging.debug('[%s] Process output -> length = %s' % (self.id, len(self.output)))
                self.__deleteFile(self.__logfile)
            except:
                logging.error('[%s] Failed to read capture log file -> %s' % (self.id, self.__logfile))
        if self.__file is not None:  # with config file
            for file in self.__file:
                self.__deleteFile(file['path'])
