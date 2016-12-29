# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import platform
import argparse
import os
import time
from . import workarea as wa

uptime = time.time()
#channels = []
admins = {}
coremodules = {}
networks = {}
stores = {}
args = argparse.ArgumentParser()
daemon = False
irc = None


if platform.system() == 'Linux':
    HOME = os.environ['HOME']
elif platform.system() == 'Windows':
    HOME = os.environ['USERPROFILE']

workarea = wa.workarea(os.path.join(HOME, '.simpbot'),
    {'files': ['admins.ini'], 'dirs': ['logs', 'modules', 'data']})
#os.chdir(workarea.abspath)
modules = workarea.new_wa('modules')
servers = workarea.new_wa('servers')
adminspath = workarea.join('admins.ini')
logs = workarea.new_wa('logs')
data = workarea.new_wa('data')
dbstore = data.new_wa('dbstore')
ctrl = data.new_wa('commands')
