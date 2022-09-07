#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from enum import Enum
from Utils.Logger import logger
from Utils.Common import genFlag
from Utils.Exception import managerException


class TASK(Enum):  # task status
    LOADED = -1
    RUNNING = 0
    FINISH = 1


class Task(object):
    """ Manage global check task.
    """
    __tasks = {}  # task status -> loaded / running / complete
    __unions = {}  # one union include multi tasks

    def __init__(self):
        logger.info('Manager start')

    def listUnion(self) -> list:  # get all union ids
        return [x for x in self.__unions]

    def isUnion(self, unionId: str) -> bool:  # check if the union id exist
        return unionId in self.__unions

    def addUnion(self, union: list) -> str:  # add union to manager (include multi tasks)
        tasks = {}  # temporary task storage
        taskIds = []  # task id list for manage union
        unionId = genFlag(length = 12)  # generate union id (12 bytes)
        logger.debug('Manager start to load union [%s]' % unionId)
        for task in union:
            taskId = genFlag(length = 16)  # generate task id (16 bytes)
            taskIds.append(taskId)
            tasks[taskId] = {
                'status': TASK.LOADED,  # task status -> loaded
                'data': copy.deepcopy(task)  # save task info
            }
            logger.info('Manager add task [%s] -> %s' % (taskId, task))
        self.__tasks.update(tasks)  # load into task list
        self.__unions[unionId] = {
            'finish': False,
            'items': taskIds  # record task items
        }
        logger.info('Manager add union [%s] -> %s' % (unionId, taskIds))
        return unionId

    def delUnion(self, unionId) -> None:  # remove union
        if unionId not in self.__unions:
            logger.error('Manager union [%s] not found' % unionId)
            raise managerException('Union id not found')
        if not self.__unions[unionId]['finish']:  # some tasks are still running
            raise managerException('Couldn\'t remove working union')
        self.__unions.pop(unionId)

    def getUnion(self, unionId: str) -> dict:  # get union status (remove tasks when all completed)
        if unionId not in self.__unions:
            logger.error('Manager union [%s] not found' % unionId)
            raise managerException('Union id not found')
        if self.__unions[unionId]['finish']:  # all tasks are finished
            return self.__unions[unionId]
        tasks = self.__unions[unionId]['items']
        finishNum = 0
        for taskId in tasks:
            if self.__tasks[taskId]['status'] == TASK.FINISH:  # get number of completed task
                finishNum += 1
        logger.info('Manager statistics union [%s] -> %i/%i' % (unionId, finishNum, len(tasks)))
        if finishNum < len(tasks):  # some tasks are not yet completed
            logger.debug('Manager union [%s] still working' % unionId)
            return {
                'finish': False,
                'percent': round(finishNum / len(tasks), 2)
            }
        self.__unions[unionId]['result'] = []
        for taskId in tasks:
            task = self.__tasks[taskId]
            self.__tasks.pop(taskId)  # remove from task list
            self.__unions[unionId]['result'].append(task['data'])
        self.__unions[unionId]['finish'] = True
        self.__unions[unionId].pop('items')
        logger.info('Manager release union [%s] -> %s' % (unionId, self.__unions[unionId]['result']))
        return self.__unions[unionId]

    def popTask(self) -> tuple[str or None, any]:  # fetch a loaded task
        for taskId, task in self.__tasks.items():
            if task['status'] != TASK.LOADED: continue  # only get loaded task
            task['status'] = TASK.RUNNING  # set task status as running
            logger.info('Manager pop task [%s] -> %s' % (taskId, task['data']))
            return taskId, copy.deepcopy(task['data'])
        logger.debug('Manager has no more task')
        raise managerException('No more tasks')

    def finishTask(self, taskId: str, taskData: dict) -> None:  # update task data when completed
        if taskId not in self.__tasks:
            logger.error('Manager task [%s] not found' % taskId)
            raise managerException('Task id not found')
        self.__tasks[taskId]['data'] = copy.deepcopy(taskData)
        self.__tasks[taskId]['status'] = TASK.FINISH  # set task status as completed


Manager = Task()  # global task manager
