#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
from Basis.Logger import logging
from Basis.Functions import genFlag


class Task(object):
    """ Manage global check task.
    """
    __tasks = {}
    __subTasks = {}  # sub task status -> loaded / running / complete

    def __init__(self):
        logging.info('task manager start')

    def addTask(self, tasks: list) -> str:  # add task to manager (multi sub tasks)
        subTasks = {}
        subTaskIds = []
        for subTask in tasks:
            subTaskId = genFlag(length = 24)  # generate sub task id (24 bytes)
            subTaskIds.append(subTaskId)
            subTasks[subTaskId] = {
                'status': 'loaded',
                'data': copy.deepcopy(subTask)
            }
            logging.info('add sub task %s -> %s' % (subTaskId, subTasks[subTaskId]['data']))
        taskId = genFlag(length = 16)  # generate task id (16 bytes)
        self.__tasks[taskId] = {  # load task
            'sub': subTaskIds
        }
        self.__subTasks.update(subTasks)  # load sub tasks
        logging.info('task %s loaded' % taskId)
        return taskId

    def isTask(self, taskId: str) -> bool:  # check if the task id exist
        return taskId in self.__tasks

    def getTask(self, taskId: str) -> dict:  # get task status (remove sub tasks when all completed)
        if taskId not in self.__tasks:
            logging.error('task id %s not found' % taskId)
            raise RuntimeError('task id not found')
        subList = self.__tasks[taskId]['sub']
        completed = 0
        for subTaskId in subList:
            if self.__subTasks[subTaskId]['status'] == 'complete':  # get number of completed sub task
                completed += 1
        logging.debug('[%s] statistics sub task status -> %i/%i' % (taskId, completed, len(subList)))
        if completed < len(subList):  # some sub tasks are not completed
            logging.debug('[%s] task still running' % taskId)
            return {
                'done': False,
                'total': len(subList),
                'finish': completed,
            }
        logging.debug('[%s] task work complete' % taskId)  # all sub tasks completed
        result = []
        for subTaskId in subList:
            subTask = self.__subTasks[subTaskId]
            self.__subTasks.pop(subTaskId)
            result.append(subTask['data'])
        logging.debug('release sub tasks -> %s' % result)
        return {
            'done': True,
            'result': result
        }

    def listTask(self) -> list:  # get all task ids
        return [x for x in self.__tasks]

    def popSubTask(self) -> tuple[str or None, any]:  # fetch a loaded sub task
        for subTaskId, subTask in self.__subTasks.items():
            if subTask['status'] != 'loaded': continue  # only get loaded sub task
            subTask['status'] = 'running'  # set status as running
            return subTaskId, copy.deepcopy(subTask['data'])
        return None, None

    def updateSubTask(self, subTaskId: str, subTaskData: dict) -> None:  # update sub task data when completed
        if subTaskId not in self.__subTasks:
            logging.error('sub task id %s not found' % subTaskId)
            raise RuntimeError('sub task id not found')
        self.__subTasks[subTaskId]['data'] = copy.deepcopy(subTaskData)
        self.__subTasks[subTaskId]['status'] = 'complete'


Manage = Task()  # global task manager
