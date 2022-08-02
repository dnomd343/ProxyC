#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Basis.Logger import logging
from Basis.Functions import genFlag


class Task(object):
    """ Manage global check task.
    """
    __tasks = {}  # task status -> loaded / running / complete
    __unions = {}  # one union include multi tasks
    __TASK_LOADED = -1
    __TASK_RUNNING = 0
    __TASK_FINISH = 1

    def __init__(self):
        logging.info('Manager start')

    def listUnion(self) -> list:  # get all union ids
        return [x for x in self.__unions]

    def isUnion(self, unionId: str) -> bool:  # check if the union id exist
        return unionId in self.__unions

    def addUnion(self, union: list) -> str:  # add union to manager (include multi tasks)
        tasks = {}  # temporary task storage
        taskIds = []  # task id list for manage union
        unionId = genFlag(length = 12)  # generate union id (12 bytes)
        logging.debug('Manager start to load union [%s]' % unionId)
        for task in union:
            taskId = genFlag(length = 16)  # generate task id (16 bytes)
            taskIds.append(taskId)
            tasks[taskId] = {
                'status': self.__TASK_LOADED,  # task status -> loaded
                'data': copy.deepcopy(task)  # save task info
            }
            logging.info('Manager add task [%s] -> %s' % (taskId, task))
        self.__tasks.update(tasks)  # load into task list
        self.__unions[unionId] = {
            'items': taskIds  # record task items
        }
        logging.info('Manager add union [%s] -> %s' % (unionId, taskIds))
        return unionId

    def getUnion(self, unionId: str) -> dict:  # get union status (remove tasks when all completed)
        if unionId not in self.__unions:
            logging.error('Manager union [%s] not found' % unionId)
            raise RuntimeError('Union id not found')
        tasks = self.__unions[unionId]['items']
        finishNum = 0
        for taskId in tasks:
            if self.__tasks[taskId]['status'] == self.__TASK_FINISH:  # get number of completed task
                finishNum += 1
        logging.info('Manager statistics union [%s] -> %i/%i' % (unionId, finishNum, len(tasks)))
        if finishNum < len(tasks):  # some tasks are not yet completed
            logging.debug('Manager union [%s] still working' % unionId)
            return {
                'finish': False,
                'percent': '%f' % (round(finishNum / len(tasks), 2))
            }
        self.__unions.pop(unionId)  # remove from union list
        unionResult = []  # temporary storage
        for taskId in tasks:
            task = self.__tasks[taskId]
            self.__tasks.pop(taskId)  # remove from task list
            unionResult.append(task['data'])
        logging.info('Manager release union [%s] -> %s' % (unionId, unionResult))
        return {
            'finish': True,
            'result': unionResult
        }

    def popTask(self) -> tuple[str or None, any]:  # fetch a loaded task
        for taskId, task in self.__tasks.items():
            if task['status'] != self.__TASK_LOADED: continue  # only get loaded task
            task['status'] = self.__TASK_RUNNING  # set task status as running
            logging.info('Manager pop task [%s] -> %s' % (taskId, task['data']))
            return taskId, copy.deepcopy(task['data'])
        logging.debug('Manager has no more loaded tasks')
        raise RuntimeError('No more tasks')

    def finishTask(self, taskId: str, taskData: dict) -> None:  # update task data when completed
        if taskId not in self.__tasks:
            logging.error('Manager task [%s] not found' % taskId)
            raise RuntimeError('Task id not found')
        self.__tasks[taskId]['data'] = copy.deepcopy(taskData)
        self.__tasks[taskId]['status'] = self.__TASK_FINISH  # set task status as completed


Manager = Task()  # global task manager
