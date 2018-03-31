# coding=utf8
"""
database/user.py - backend of the user database.

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
from simpbot.settings import STRING, FLOAT, INT, BOOL, PICKLE, USER_UNIQ_STATUS
from simpbot.settings import CACHE_DURATION_USER, CACHE_DURATION_USER_PROPERTIES
from simpbot.database import getDatabase, __uuid__
from simpbot.database import cache
from simpbot.database.cache import mapper
# </simpbot framework>

logger = logger.getLogger(__name__)
Trigger = trigger.getTrigger(__name__)
Cache = cache.getCache(__name__)
database = getDatabase(__uuid__, catch=True)
User = database.getTable('User')
Properties = database.getTable('User_Properties')
Status = database.getTable('User_Lock')


@Cache.cache(dict(
    link=mapper.argsmap(uuid=0),
    store=dict(
        key=mapper.argsmap(__result='attr:uuid'),
        store='all',
        skip=(None,)),
    duration=CACHE_DURATION_USER))
def getby_uuid(uuid):
    try:
        return User.get(User.uuid == uuid)
    except User.DoesNotExist:
        return


@Cache.cache(dict(
    link=mapper.argsmap(network=0, nickname=1),
    store=dict(
        key=mapper.argsmap(__result='attr:uuid'),
        store='all',
        skip=(None,)),
    duration=CACHE_DURATION_USER))
def getby_nickname(network, nickname):
    try:
        return User.get(User.network == network and User.nickname == nickname)
    except User.DoesNotExist:
        return


@Cache.cache(dict(
    link=mapper.argsmap(network=0, hostname=1),
    store=dict(
        key=mapper.argsmap(__result='attr:uuid'),
        store='all',
        skip=(None,)),
    duration=CACHE_DURATION_USER))
def getby_hostname(network, hostname):
    try:
        return User.get(User.network == network and User.hostname == hostname)
    except User.DoesNotExist:
        return


@Cache.cache(dict(
    link=mapper.argsmap(network=0, username=1),
    store=dict(
        key=mapper.argsmap(__result='attr:uuid'),
        store='all',
        skip=(None,)),
    duration=CACHE_DURATION_USER))
def getby_username(network, username):
    try:
        return User.get(User.network == network and User.username == username)
    except User.DoesNotExist:
        return


@Cache.cache(dict(
    link=mapper.argsmap(account=(0, 'attr:uuid'), varname=1),
    store=dict(
        key=mapper.argsmap(account=(0, 'attr:uuid'), varname=1),
        store='all'),
    duration=CACHE_DURATION_USER_PROPERTIES))
@Trigger.trigger('get_properties')
def get_properties(account, varname):
    try:
        propertie = Properties.get(
            (Properties.account == account) and
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
            info = {}
            info['network'] = account.network.name
            if account.hostname:
                info['hostname'] = account.hostname
            if account.nickname:
                info['nickname'] = account.nickname
            if account.username:
                info['username'] = account.username
            info = ', '.join(['{0}: {1}'.format(*i) for i in info.items()])
            logger.warning("%s | Variable '%s' contains unrecoverable data.", info, varname)
            return
    return value


@Trigger.trigger('set_properties')
def set_properties(account, varname, varvalue):
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

    var = get_properties(account, varname)
    if var is None:
        Properties.create(
            account=account,
            varname=varname,
            varvalue=varvalue,
            vartype=vartype,
            date=datetime.datetime.now())
    else:
        var.varvalue = varvalue
        var.vartype = vartype
        var.date = datetime.datetime.now()
        var.save()
    cache.del_object(get_properties.m_key.generate((account, varname), {}))


@Cache.cache(dict(
    uniq=USER_UNIQ_STATUS,
    link=mapper.argsmap(account=(0, 'attr:uuid')),
    store=dict(
        key=mapper.argsmap(account=(0, 'attr:uuid')),
        store='all'),
    duration=CACHE_DURATION_USER_PROPERTIES))
def status(account):
    return Status.get(Status.account == account)


@Trigger.trigger('lock')
def lock(admin, account, reason):
    stt = status(account)
    if stt.locked is True:
        return False
    stt.locked = True
    stt.locked_by = admin
    stt.lock_reason = reason
    stt.date = datetime.datetime.now()
    stt.save()
    cache.del_object(status.m_key.generate((account,), {}))


@Trigger.trigger('unlock')
def unlock(admin, account):
    stt = status(account)
    if stt.locked is True:
        return False
    stt.locked = False
    stt.locked_by = admin
    stt.lock_reason = None
    stt.date = datetime.datetime.now()
    stt.save()
    cache.del_object(status.m_key.generate((account,), {}))


@Trigger.trigger('create')
def create(network, **kwargs):
    account = User.create(network=network, **kwargs['basic'])
    for propertie in kwargs['properties']:
        if isinstance(propertie['varvalue'], string_types):
            propertie['vartype'] = STRING
        elif isinstance(propertie['varvalue'], int):
            propertie['vartype'] = INT
        elif isinstance(propertie['varvalue'], float):
            propertie['vartype'] = FLOAT
        elif isinstance(propertie['varvalue'], bool):
            propertie['vartype'] = BOOL
        else:
            propertie['varvalue'] = cPickle.dumps(propertie['varvalue'])
            propertie['vartype'] = PICKLE
        Properties.create(account=account, **propertie)
    Status.create(account=account)


@Trigger.trigger('drop')
def drop(account):
    cache.del_object(getby_uuid.m_key.generate((account,), {}))
    account.delete_instance()
