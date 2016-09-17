# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import platform
import os
import time
from . import workarea as wa

uptime = time.time()
DAEMON = False
irc = None


if platform.system() == 'Linux':
    HOME = os.environ['HOME']
elif platform.system() == 'Windows':
    HOME = os.environ['USERPROFILE']

workarea = wa.workarea(os.path.join(HOME, '.simpbot'),
    {'files': ['config.py'], 'dirs': ['logs', 'modules', 'data']})
#os.chdir(workarea.abspath)
modules = workarea.new_wa('modules')
logs = workarea.new_wa('logs')
data = workarea.new_wa('data')
CONFPATH = workarea.join('config.py')