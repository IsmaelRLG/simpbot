# coding=utf8
"""
logger.py - simple irc bot.

Copyright © 2016-2018, Ismael Lugo, <ismaelrlgv@gmail.com>
Licensed under the MIT License.
"""

from __future__ import absolute_import, unicode_literals

__version__ = "18.3.21"
__author__ = 'Ismael Lugo (kwargs) <ismaelrlgv@gmail.com>'

import importlib

try:
    requires = "six flask prettytable httplib2"
    map(importlib.import_module(), requires.split())
except ImportError as error:
    pass
else:
    from . import settings
    from . import workarea
    from . import envvars


    modules = moduletools.core.coremod()
    get_module = modules.get_module

    #lint:disable
    from . import commands
    from . import connections
    from . import api
    from . import cli
    #lint:enable
