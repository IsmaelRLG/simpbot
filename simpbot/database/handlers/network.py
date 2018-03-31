# coding=utf8
"""
database/handlers/user.py - handlers for database/user.py.

Copyright © 2016-2018, Ismael Lugo, <ismaelrlgv@gmail.com>
Licensed under the MIT License.
"""
from __future__ import absolute_import, unicode_literals

from simpbot.database import user
from simpbot.database import channel
from simpbot.database.user import User
from simpbot.database.channel import Channel
from simpbot.database.network import Trigger
from simpbot.settings import BEFORE
from simpbot.settings import TGR_CONTINUE, TGR_SKIP, TGR_STOP, TGR_BREAK


def remove_channels(status):
    net = status.get(network=0)[0]
    for chan in Channel.select().where(Channel.network == net):
        channel.drop(chan)
    return TGR_CONTINUE


def remove_users(status):
    net = status.get(network=0)[0]
    for account in User.select().where(User.network == net):
        user.drop(account)
    return TGR_CONTINUE


def remove_admins(status):
    pass


Trigger.add('delete', remove_channels,  10, BEFORE)
Trigger.add('delete', remove_users,     20, BEFORE)
Trigger.add('delete', remove_admins,    30, BEFORE)
