# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import platform
import argparse
import os
import time
import sys
from . import workarea as wa


uptime = time.time()
#channels = []
admins = {}
coremodules = {}
networks = {}
stores = {}
args = argparse.ArgumentParser()
default_lang = 'es'
daemon = False
irc = None
cfg_kwargs = {}
if sys.version_info[0:2] >= (3, 2):
    cfg_kwargs['inline_comment_prefixes'] = (';',)

if platform.system() == 'Linux':
    HOME = os.environ['HOME']

    def getlang():
        lang = os.environ['LANG']
        lang = lang.split('.')[0]
        from . import localedata
        if localedata.simplocales.exists(lang, 'fullsupport'):
            return lang
        if '_' in lang:
            lang = lang.split('_')[0]
            if localedata.simplocales.exists(lang, 'fullsupport'):
                return lang
            else:
                return default_lang
        else:
            return default_lang
    default_lang = getlang()


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

if workarea.exists('default_lang'):
    default_lang = workarea.file('default_lang', 'r').read()
