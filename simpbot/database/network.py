# coding=utf8
"""
database/network.py - --EDIT THIS--

Copyright © 2016-2018, Ismael Lugo, <ismaelrlgv@gmail.com>
Licensed under the MIT License.
"""

from __future__ import absolute_import, unicode_literals

import datetime
from six import string_types
from six.moves import cPickle
# <simpbot framework>
from simpbot import logger
from simpbot import trigger
from simpbot.database import getDatabase, __uuid__
from simpbot.database import cache
from simpbot.settings import STRING, FLOAT, INT, BOOL, PICKLE
from simpbot.settings import DEFAULT_PORT, DEFAULT_SSL
from simpbot.database.cache import mapper
# </simpbot framework>

Cache = cache.getCache(__name__, up_to_date=False)
Trigger = trigger.getTrigger(__name__)
Logger = logger.getLogger(__name__)
database = getDatabase(__uuid__, catch=True)
Network = database.getTable('Network')
Properties = database.getTable('Network_Properties')


@Cache.cache(dict(
    link=mapper.argsmap(network=(0, 'attr:uuid'), varname=1),
    store=dict(
        key=mapper.argsmap(network=(0, 'attr:uuid'), varname=1),
        store='all',
        skip=(None,))))
@Trigger.trigger('get_properties')
def get_properties(network, varname):
    try:
        propertie = Properties.get(
            (Properties.network == network) and
            (Properties.varname == varname))
    except Properties.DoesNotExist:
        return

    value = propertie.value
    if propertie.vartype == STRING:
        pass
    elif propertie.vartype == INT:
        value = int(propertie.value)
    elif propertie.vartype == FLOAT:
        value = float(propertie.value)
    elif propertie.vartype == BOOL:
        value = bool(propertie.value)
    elif propertie.vartype == PICKLE:
        try:
            value = cPickle.loads(propertie.value)
        except Exception:
            info = network.name
            logger.warning("%s | Variable '%s' contains unrecoverable data.", info, varname)
            return
    return value


@Trigger.trigger('set_properties')
def set_properties(network, varname, varvalue):
    if isinstance(varvalue, string_types):
        vartype = STRING
    elif isinstance(varvalue, int):
        vartype = INT
    elif isinstance(varvalue, float):
        vartype = FLOAT
    elif isinstance(varvalue, bool):
        vartype = BOOL
    else:
        varvalue = cPickle.dumps(varvalue)
        vartype = PICKLE

    var = get_properties(network, varname)
    if var is None:
        Properties.create(
            network=network,
            varname=varname,
            varvalue=varvalue,
            vartype=vartype,
            date=datetime.datetime.now())
    else:
        var.varvalue = varvalue
        var.vartype = vartype
        var.date = datetime.datetime.now()
        var.save()
    cache.del_object(get_properties.m_key.generate((network, varname), {}))


@Trigger.trigger('create')
def create(name, host, port=DEFAULT_PORT, ssl=DEFAULT_SSL, password=None):
    network = Network.create(
        name=name, host=host, port=port,
        ssl=ssl, password=password)
    return network


@Trigger.trigger('delete')
def delete(network):
    network.delete_instance()


@Trigger.trigger('change_status')
def change_status(network, status):
    network.active = status
    network.save()


@Cache.cache({'store': {'store': 'all', 'skip': (None,)}})
@Trigger.trigger('change_status')
def list():
    return tuple(Network.select())
