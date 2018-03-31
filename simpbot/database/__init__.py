# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)
from __future__ import absolute_import

from . import models
from . import cache
from . import network
from . import user
from . import channel
from . import config

db_list = {}
__version__ = '0.1.0'
__uuid__ = 'c8972e76-095e-443f-bf6e-7a6d1b02339c'


def getDatabase(name, catch=False):
    if catch:
        try:
            return db_list[name]
        except KeyError:
            class dummy:
                def getTable(self):
                    pass
            return dummy()
    else:
        return db_list[name]


def setDatabase(name, db):
    if name in db_list:
        raise models.DatabaseError('Duplicate database name: ', name)
    db_list[name] = db
