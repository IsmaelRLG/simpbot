# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import platform
import os
from . import workarea as wa

DAEMON = False
irc = None


if platform.system() == 'Linux':
    HOME = os.environ['HOME']
elif platform.system() == 'Windows':
    HOME = os.environ['????']

workarea = wa.workarea(os.path.join(HOME, '.simpbot'),
    {'files': ['config.py'], 'dirs': ['logs', 'modules']})
#os.chdir(workarea.abspath)
modules = workarea.new_wa('modules')
logs = workarea.new_wa('logs')
CONFPATH = workarea.join('config.py')