# coding=utf8
"""
database/handlers/user.py - handlers for database/user.py.

Copyright © 2016-2018, Ismael Lugo, <ismaelrlgv@gmail.com>
Licensed under the MIT License.
"""
from __future__ import absolute_import, unicode_literals


from simpbot.database import user
from simpbot.database import channel
from simpbot.database.user import Status
from simpbot.database.user import Properties as User_Properties
from simpbot.database.channel import Flags
from simpbot.settings import BEFORE, AFTER
from simpbot.settings import TGR_CONTINUE, TGR_SKIP, TGR_STOP, TGR_BREAK


def account(status):
    status.account = status.get(account=0)[0]
    return TGR_SKIP


def remove_admin(status):
    pass


def remove_channels(status):
    # Removing founded channels
    F_channels = Flags.select(Flags.channel).where(
        (Flags.account == status.account) &
        (Flags.founder == True))
    flags = Flags.select(Flags.channel).where(
        (Flags.account == status.account)
    )
    for chan in F_channels:
        channel.drop(chan, successor=True)

    for chan in flags:
        channel.flags(channel, status.account, '-*', all=True)
    return TGR_CONTINUE


def remove_properties(status):
    query = User_Properties.select().where(
        (User_Properties.account == status.account)
    )
    key = user.get_properties.m_key
    for var in query:
        user.cache.del_object(key.generate((status.account, var.varname), {}))
    User_Properties.delete().where(User_Properties.account == status.account).execute()
    return TGR_CONTINUE


def remove_status(status):
    Status.delete().where(Status.account == status.account).execute()
    user.cache.del_object(user.status.m_key.generate((status.account,), {}))
    return TGR_CONTINUE


user.Trigger.add('drop', account,            5, BEFORE)
user.Trigger.add('drop', remove_admin,      10, BEFORE)
user.Trigger.add('drop', remove_channels,   20, BEFORE)
user.Trigger.add('drop', remove_properties, 30, BEFORE)
user.Trigger.add('drop', remove_status,     40, BEFORE)
