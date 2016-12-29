# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

__version__ = "1.7.7"
__author__ = 'Ismael Lugo (kwargs)'

#lint:disable
import workarea
import envvars
import bottools
import features
import parser
import mode
import buffer
import irc
import handlers
import request
import admins
import dbstore
import control
import moduletools
#lint:enable

modules = moduletools.core.coremod()
get_module = modules.get_module

#lint:disable
import commands
import connections
#lint:enable