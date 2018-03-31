# coding=utf8
"""
database/channel.py - backend of the channel database.

Copyright © 2016-2018, Ismael Lugo, <ismaelrlgv@gmail.com>
Licensed under the MIT License.
"""

from __future__ import absolute_import, unicode_literals

import uuid
import datetime
from six import string_types
from six.moves import cPickle

# <simpbot framework>
from simpbot import mode
from simpbot import logger
from simpbot import trigger
from simpbot import settings as se
from simpbot.settings import STRING, FLOAT, INT, BOOL, PICKLE
from simpbot.settings import CACHE_DURATION_CHANNEL_PROPERTIES
from simpbot.settings import CACHE_DURATION_CHANNEL, CHANNEL_UNIQ_STATUS
from simpbot.database import getDatabase, __uuid__
from simpbot.database import cache
from simpbot.database.cache import mapper
# </simpbot framework>

logger = logger.getLogger(__name__)
Trigger = trigger.getTrigger(__name__)
Cache = cache.getCache(__name__)
database = getDatabase(__uuid__, catch=True)
Channel = database.getTable('Channel')
Properties = database.getTable('Channel_Properties')
Flags = database.getTable('Channel_Flags')
Templates = database.getTable('Channel_Templates')
Status = database.getTable('Channel_Lock')


@Cache.cache(dict(
    link=mapper.argsmap(network=(0, 'attr:uuid'), channel=1),
    store=dict(
        key=mapper.argsmap(__result='attr:uuid'),
        store='all',
        skip=(None,)),
    duration=CACHE_DURATION_CHANNEL))
def get(network, channel):
    try:
        return Channel.get(
            (Channel.network == network) &
            (Channel.name == channel.lower()))
    except Channel.DoesNotExist:
        return


@Cache.cache(dict(
    link=mapper.argsmap(channelt=(0, 'attr:uuid'), varname=1),
    store=dict(
        key=mapper.argsmap(channel=(0, 'attr:uuid'), varname=1),
        store='all'),
    duration=CACHE_DURATION_CHANNEL_PROPERTIES))
@Trigger.trigger('get_properties')
def get_properties(channel, varname):
    try:
        propertie = Properties.get(
            (Properties.channel == channel) and
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
            info = '{channel.network.name}: {channel.name}'
            info = info.format(channel=channel)
            logger.warning("%s | Variable '%s' contains unrecoverable data.", info, varname)
            return
    return value


@Trigger.trigger('set_properties')
def set_properties(channel, varname, varvalue):
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

    var = get_properties(channel, varname)
    if var is None:
        Properties.create(
            channel=channel,
            varname=varname,
            varvalue=varvalue,
            vartype=vartype,
            date=datetime.datetime.now())
    else:
        var.varvalue = varvalue
        var.vartype = vartype
        var.date = datetime.datetime.now()
        var.save()
    cache.del_object(get_properties.m_key.generate((channel, varname), {}))


@Cache.cache(dict(
    uniq=CHANNEL_UNIQ_STATUS,
    link=mapper.argsmap(channel=(0, 'attr:uuid')),
    store=dict(
        key=mapper.argsmap(channel=(0, 'attr:uuid')),
        store='all'),
    duration=CACHE_DURATION_CHANNEL_PROPERTIES))
def status(channel):
    return Status.get(Status.account == channel)


@Trigger.trigger('lock')
def lock(admin, channel, reason):
    stt = status(channel)
    if stt.locked is True:
        return False
    stt.locked = True
    stt.locked_by = admin
    stt.lock_reason = reason
    stt.date = datetime.datetime.now()
    stt.save()
    cache.del_object(status.m_key.generate((channel,), {}))


@Trigger.trigger('unlock')
def unlock(admin, channel):
    stt = status(channel)
    if stt.locked is True:
        return False
    stt.locked = False
    stt.locked_by = admin
    stt.lock_reason = None
    stt.date = datetime.datetime.now()
    stt.save()
    cache.del_object(status.m_key.generate((channel,), {}))


@Trigger.trigger('create')
def create(network, channel):
    return Channel.create(network=network, name=channel.lower())


@Trigger.trigger('drop')
def drop(channel):
    cache.del_object(get.m_key.generate((channel.network, channel.name), {}))
    channel.delete_instance()


@Trigger.trigger('drop_confirmation')
def drop_confirmation(channel):
    hash = get_properties(channel, se.VAR_CONFIRMDROP)
    if hash is None:
        hash = uuid.uuid4().hex
        set_properties(channel, se.VAR_CONFIRMDROP, hash)
    return hash


@Cache.cache(dict(
    link=mapper.argsmap(channel=(0, 'attr:uuid'), account=(1, 'attr:uuid')),
    store=dict(
        key=mapper.argsmap(channel=(0, 'attr:uuid'), account=(1, 'attr:uuid')),
        store='all'),
    duration=CACHE_DURATION_CHANNEL_PROPERTIES))
def get_flags(channel, account):
    try:
        flags = Flags.get(
        (Flags.channel == channel) &
        (Flags.account == account))
    except Flags.DoesNotExist:
        return None

    _flags = ''
    if flags.founder is True:
        _flags += se.FLAG_FOUNDER
    elif flags.successor is True:
        _flags += se.FLAG_SUCCESSOR

    if flags.template:
        _flags += flags.template.value
    else:
        _flags += flags.value
    return _flags


@Trigger.trigger('set_flags')
def set_flags(channel, account, value, founder=None, successor=None):
    _flags = []
    f_type = 0
    v_type = 0
    try:
        flags = Flags.get(
        (Flags.channel == channel) &
        (Flags.account == account))
    except Flags.DoesNotExist:
        flags = None
    else:
        if flags.template:
            f_type = +1
            _flags.extend(list(flags.template.value))
        else:
            _flags.extend(list(flags.value))

    if se.FLAGS_ADD in value or se.FLAGS_DEL in value:
        if value == se.FLAGS_DEL + '*':
            del _flags[:]
        else:
            gen = mode._parse_modes(value, only=''.join(se.FLAGS))
            for sign, flag, null in gen:
                if sign == se.FLAGS_ADD:
                    if flag not in _flags:
                        _flags.append(flag)
                else:
                    if flag in _flags:
                        _flags.remove(flag)
    elif value is not None:
        try:
            v_type += 1
            _template = Templates.get(
            (Templates.channel == channel) & (Templates.name == value))
        except Templates.DoesNotExist:
            return False

    if flags:
        e = True
        flags.founder = founder
        flags.successor = successor
        if v_type == 1:
            flags.template = _template
            if f_type == 0:
                flags.value = None
        elif v_type == 0:
            if len(_flags) > 0:
                flags.delete_instance()
                e = False
            else:
                flags.value = ''.join(_flags)
                if f_type == 1:
                    flags.template = None
        if e:
            flags.date = datetime.datetime.now()
            flags.save()
        cache.del_object(get_flags.m_key.generate((channel, account), {}))
    else:
        if len(_flags) > 0 and v_type == 0:
            return

        Flags.create(
            channel=channel,
            account=account,
            template=(_template if v_type == 1 else None),
            value=(''.join(_flags) if v_type == 0 else None),
            founder=founder,
            successor=successor,
            date=datetime.datetime.now())
