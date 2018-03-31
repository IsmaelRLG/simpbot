# coding=utf8
"""
database/config.py - --EDIT THIS--

Copyright © 2016-2018, Ismael Lugo, <ismaelrlgv@gmail.com>
Licensed under the MIT License.
"""

from __future__ import absolute_import, unicode_literals

from six import string_types
from six.moves import cPickle

from simpbot import trigger
from simpbot import settings as s
from simpbot.settings import STRING, FLOAT, INT, BOOL, PICKLE
from simpbot.database import cache
from simpbot.database import getDatabase, __uuid__
from simpbot.database.cache import mapper

Trigger = trigger.getTrigger(__name__)
Cache = cache.getCache(__name__, up_to_date=False)
database = getDatabase(__uuid__, catch=True)
Config = database.getTable('Config') if database is not None else None


@Cache.cache(dict(
    link=mapper.argsmap(varname=0),
    store=dict(
        key=mapper.argsmap(varname=0),
        store='all')))
def get(varname, default=None, settings=True):
    try:
        var = Config.get(Config.varname == varname)
    except Config.DoesNotExist:
        if settings:
            try:
                return s.get(varname)
            except KeyError:
                return default
        else:
            return default

    if var.vartype == STRING:
        value = var.varvalue
    elif var.vartype == INT:
        value = int(var.varvalue)
    elif var.vartype == FLOAT:
        value = float(var.varvalue)
    elif var.vartype == BOOL:
        value = bool(var.varvalue)
    elif var.vartype == PICKLE:
        value = cPickle.loads(var.varvalue)
    else:
        raise TypeError('Unknown vartype of %s' % varname)
    return value


@Trigger.trigger('set')
def set(varname, varvalue, description=None):
    try:
        var = Config.get(Config.varname == varname)
    except Config.DoesNotExist:
        var = None

    if isinstance(varvalue, string_types):
        vartype = STRING
    elif isinstance(varvalue, int):
        vartype = INT
    elif isinstance(varvalue, float):
        vartype = FLOAT
    elif isinstance(varvalue, bool):
        vartype = BOOL
    else:
        vartype = PICKLE
        varvalue = cPickle.dumps(varvalue)

    if var is None:
        Config.create(
            varname=varname,
            varvalue=varvalue,
            vartype=vartype,
            description=description)
    else:
        var.varvalue = varvalue
        var.vartype = vartype
        var.description = description
        var.save()

    cache.del_object(get.m_key.generate((varname,), {}))
