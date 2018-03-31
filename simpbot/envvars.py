# coding=utf8
"""
envvars.py - --EDIT THIS--

Copyright © 2016-2018, Ismael Lugo, <ismaelrlgv@gmail.com>
Licensed under the MIT License.
"""

from __future__ import absolute_import, unicode_literals

import os
import time
import locale
from simpbot import workarea as wa
from simpbot import settings as se

workarea = wa.workarea(
    os.path.join(os.environ['HOME'], se.MAIN_DIR),
    {
        'files': [se.FILE_SETTINGS],
        'dirs': [se.MAIN_LOG_DIR, se.MAIN_MODULES_DIR, se.MAIN_MODDATA_DIR]
    }
)

os.chdir(workarea.abspath)
moddata = workarea.new_wa(se.MAIN_MODDATA_DIR)
modules = workarea.new_wa(se.MAIN_MODULES_DIR)
log = workarea.new_wa(se.MAIN_LOG_DIR)
log_bot = log.new_wa(se.SUB_LOG_DIR_BOT)
log_irc = log.new_wa(se.SUB_LOG_DIR_IRC)

log_abspath = log_bot.join(se.LOG_FILENAME)
settings_file = workarea.join(se.FILE_SETTINGS)
mods_path = [modules.abspath]
uptime = time.time()
api_started = False
daemon = False
loggers = {}


def getlang():
    lang = locale.getdefaultlocale()[0]
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


if workarea.exists(simpbotcfg) and workarea.isfile(simpbotcfg):
    from simpbot.simpleconf import ReadConf
    cfg = ReadConf(workarea.join(simpbotcfg))
    default_lang = cfg.get('DEFAULT_LANG', default_lang)
else:
    class cfg:
        def get(self, opt, default=None):
            return default
        getint = get
        getboolean = get
    cfg = cfg()
