# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

__version__ = "1.8"
__author__ = 'Ismael Lugo (kwargs)'

try:
    __import__('six')
except:
    pass
else:
    #lint:disable
    from . import workarea
    from . import envvars
    from . import localedata
    from . import bottools
    from . import features
    from . import parser
    from . import mode
    from . import buffer
    from . import irc
    from . import handlers
    from . import request
    from . import admins
    from . import dbstore
    from . import control
    from . import moduletools
    #lint:enable

    modules = moduletools.core.coremod()
    get_module = modules.get_module

    #lint:disable
    from . import commands
    from . import connections
    #lint:enable