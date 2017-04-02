# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import time
import sys
from six.moves import _thread
from simpbot import envvars
from simpbot import __version__


def ascii(start='#'):
    head = ''
    head += '{0}  ____  _  __    _______  ____   ______________\n'
    head += '{0} / ___|(_)|  \  /   ___ \| __ \ / _ \___   ___/\n'
    head += '{0} | |__ | ||   \/   |___||||__||| / \ |  | |\n'
    head += '{0} \___ \| || |\  /|  ____/| __ || | | |  | |\n'
    head += '{0} ___| || || | \/ | |     ||__||| \_/ |  | |\n'
    head += '{0}/____ /|_|| |    |_|     |____/ \___/   |_|\n'
    head += '{0}    Copyright 2016-2017, Ismael Lugo (kwargs)    v{1}\n'
    return head.format(start, __version__)


def debug(level, daemon=envvars.daemon):
    #kw = {'level': level, 'format': '%(name)s - %(levelname)s: %(message)s'}
    kw = {
        'level': level,
        'format': '%(levelname)s: %(message)s',

        # shut up excepthook!
        'stream': sys.stdout
    }
    if daemon is True:
        kw['filename'] = envvars.logs.join(time.strftime('%d%m%Y.log'))
        kw['filemode'] = 'a'
    __import__('logging').basicConfig(**kw)


def invalid_section(conf, section, options):
    status = False
    if conf.has_section(section):
        s = 0
        t = len(options)
        for option in options:
            if conf.has_option(section, option):
                s += 1
        if s != t:
            status = True
    else:
        status = True
    return status


def temp(dtime):
    return float('%.2f' % (time.time() - dtime))


def major(dtime, secs):
    return temp(dtime) > secs


def minor(dtime, secs):
    return temp(dtime) < secs


def thread(func):
    def start_thread(*args, **kwargs):
        _thread.start_new(func, args, kwargs)
    return start_thread