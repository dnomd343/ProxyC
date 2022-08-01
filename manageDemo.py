#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Basis.Manage import Manage
from Basis.Logger import logging


taskId_1 = Manage.addTask([
    {'test': 1},
    {'test': 2},
    {'test': 3},
])
logging.critical('task id 1 -> %s' % taskId_1)

taskId_2 = Manage.addTask([
    {'demo': 1},
    {'demo': 2},
    {'demo': 3},
])
logging.critical('task id 2 -> %s' % taskId_2)

logging.critical('list task -> %s' % Manage.listTask())

logging.critical('is task 1234 -> %s' % Manage.isTask('1234'))
logging.critical('is task %s -> %s' % (taskId_1, Manage.isTask(taskId_1)))

logging.critical('get task %s -> %s' % (taskId_1, Manage.getTask(taskId_1)))

subTaskId_1, subTask_1 = Manage.popSubTask()
logging.critical('pop sub task %s -> %s' % (subTaskId_1, subTask_1))
subTaskId_2, subTask_2 = Manage.popSubTask()
logging.critical('pop sub task %s -> %s' % (subTaskId_2, subTask_2))
subTaskId_3, subTask_3 = Manage.popSubTask()
logging.critical('pop sub task %s -> %s' % (subTaskId_3, subTask_3))

Manage.updateSubTask(subTaskId_3, {'test': 33})
logging.critical('update sub task %s' % subTaskId_3)
Manage.updateSubTask(subTaskId_2, {'test': 22})
logging.critical('update sub task %s' % subTaskId_2)
Manage.updateSubTask(subTaskId_1, {'test': 11})
logging.critical('update sub task %s' % subTaskId_1)

logging.critical('get task %s -> %s' % (taskId_1, Manage.getTask(taskId_1)))

subTaskId_4, subTask_4 = Manage.popSubTask()
logging.critical('pop sub task %s -> %s' % (subTaskId_4, subTask_4))

Manage.updateSubTask(subTaskId_4, {'demo': 2333})
logging.critical('update sub task %s' % subTaskId_4)

logging.critical('get task %s -> %s' % (taskId_2, Manage.getTask(taskId_2)))

logging.critical('sub task pop -> ' + str(Manage.popSubTask()))
logging.critical('sub task pop -> ' + str(Manage.popSubTask()))
logging.critical('sub task pop -> ' + str(Manage.popSubTask()))

