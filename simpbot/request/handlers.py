# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

from simpbot import mode
from simpbot.bottools import irc as irctool
from simpbot.handlers import rpl, usr
from simpbot.handlers import handler
import re
import time

################################## WHOIS #####################################


@handler(rpl(311, '!{nick} !{user} !{host} \* :!{realname}+'))
def user_rpl(irc, ev):
    irc.request.set_user(*ev('user', 'host', 'nick', 'realname'))


@handler(rpl(312, '!{nick} !{server} :!{server_info}+'))
def server(irc, ev):
    if not irc.request.has_user(ev('nick')):
        return
    irc.request.get_user(ev('nick')).set('server', ev('server', 'server_info'))


@handler(rpl(313, '!{nick} :!{msg}+'))
def ircoper(irc, ev):
    if not irc.request.has_user(ev('nick')):
        return
    irc.request.get_user(ev('nick')).set('ircoper', True)


@handler(rpl(317, '!{nick} !{lastmsg} !{since} :!{msg}'))
def idle(irc, ev):
    if not irc.request.has_user(ev('nick')):
        return
    user = irc.request.get_user(ev('nick'))
    user.lastmsg = int(ev('lastmsg'))
    user._idle = int(ev('since'))
    user.update()


@handler(rpl(318, '!{nick} :!{msg}+'))
def end_whois(irc, ev):
    if not irc.request.has_user(ev('nick')):
        return
    user = irc.request.get_user(ev('nick'))
    user.set('completed', True)


@handler(rpl(319, '!{nick} :!{channels}+'))
def channels(irc, ev):
    if not irc.request.has_user(ev('nick')):
        return

    features = irc.features
    regex = '([%s])?([%s]{1,}[^ ]+)'
    if hasattr(features, 'statusmsg') and hasattr(features, 'chantypes'):
        regex = regex % (
            re.escape(irc.features.statusmsg),
            re.escape(irc.features.chantypes))
    else:
        regex = regex % ('@\+', '#')
    # Realizar chequeo de canales...
    user = irc.request.get_user(ev('nick'))
    for modes, channel in re.findall(regex, ev('channels')):
        try:
            user.set_status(channel, 'reset', modes)
        except KeyError:
            continue
    user.update()


@handler(rpl(330, '!{nick} !{account} :is logged in as'))
def account(irc, ev):
    if not irc.request.has_user(ev('nick')):
        return
    irc.request.get_user(ev('nick')).set('account', ev('account'))


@handler(rpl(671, '!{nick} :!{msg}+'))
def ssl(irc, ev):
    if not irc.request.has_user(ev('nick')):
        return
    irc.request.get_user(ev('nick')).set('ssl', True)

################################### WHO ######################################


@handler(rpl(352, '!{data}+'))
def simpuser(irc, ev):
    regex = ('(?P<target>[^ ]+) (?P<user>[^ ]+) (?P<host>[^ ]+)'
    '( (?P<host2>[^ ]+))? (?P<server>[^ ]+) (?P<nick>[^ ]+) [HG]'
    '(?P<status>[%s]{0,}) :[0-9] (?P<realname>.+)')
    data = re.match(regex % re.escape(irc.features.statusmsg), ev('data'))
    if not data:
        return

    user = irc.request.set_user(*data.group('user', 'host', 'nick', 'realname'))
    user.set('server', data.group('server'))
    if irctool.ischannel(data.group('target'), irc=irc):
        chan = irc.request.get_chan(data.group('target'))
        chan.append(user)
        user.set_status(data.group('target'), 'reset', data.group('status'))
        user.set('completed', True)
        user.update()


@handler(rpl(354, '152 !{data}+'))
def extuser(irc, ev):
    regex = ('(?P<target>[^ ]+) (?P<user>[^ ]+) (?P<host>[^ ]+)'
    '( (?P<host2>[^ ]+))? (?P<server>[^ ]+) (?P<nick>[^ ]+) [HG]'
    '(?P<status>[%s]{0,}) (?P<account>[^ ]+) :(?P<realname>.+)')
    data = re.match(regex % re.escape(irc.features.statusmsg), ev('data'))
    if not data:
        return

    user = irc.request.set_user(*data.group('user', 'host', 'nick', 'realname'))
    user.set('server', data.group('server'))
    if data.group('account') != '0':
        user.set('account', data.group('account'))

    if irctool.ischannel(data.group('target'), irc=irc):
        chan = irc.request.get_chan(data.group('target'))
        chan.append(user)
        user.set_status(data.group('target'), 'reset', data.group('status'))
        user.set('completed', True)
        user.update()


################################ nosuch #####################################


@handler(rpl(401, '!{target} :No such nick/channel'))
def nosuch(irc, ev):
    user = irc.request.set_user(None, None, ev('target'))
    if user.host:
        user.reset()


################################# mode ######################################
triggers =  {'+': [], '-': []}
NEXT = 1
STOP = None


# MODE
@handler(usr('MODE', '!{target} !{modes}+'))
def channel_status_mode(irc, ev):
    channel = ev('target')
    if channel.lower() == irc.nickname.lower():
        return True  # user mode...
    else:
        channel = irc.request.get_chan(channel)
        if channel is None:  # wtf
            return True

    for sign, cmode, target in mode.parse_channel_modes(ev('modes')):
        for trigger in triggers[sign]:
            if trigger(irc, ev, channel, sign, cmode, target) is NEXT:
                continue
            else:
                break
    return True


def add_chan_trigger(sign, trigger):
    triggers[sign[0]].append(trigger)


def del_chan_trigger(sign, trigger):
    triggers[sign[0]].remove(trigger)
# Trigger syntax
# ------------------
#
# def func_name(irc, event, channel, sign, cmode, target):
#    * irc: IRC instance
#    * event: match of the event
#    * channel: Request Channel instance
#    * sign: signe (+ or -)
#    * cmode: channel mode
#    * target: target to change de mode
################################################################################


def trigger_user_status(irc, event, channel, sign, cmode, target):
    user = channel.get_user(target)
    if user is None:
        return NEXT

    if not hasattr(irc.features, 'modeprefix'):
        irc.features.modeprefix = {}
        for char, cmode in irc.features.prefix.items():
            irc.features.modeprefix[cmode] = char

    if not cmode in irc.features.modeprefix:
        return NEXT

    cmode = irc.features.modeprefix[cmode]
    if sign == '+':
        user.set_status(channel.channel_name, 'insert', cmode)
    else:
        user.set_status(channel.channel_name, 'remove', cmode)
    user.update()
add_chan_trigger('+', trigger_user_status)
add_chan_trigger('-', trigger_user_status)


def trigger_ban_list(irc, event, channel, sign, cmode, target):
    if cmode != 'b':
        return NEXT
    target = target.lower()
    if target in channel.list and sign == '-':
        del channel.list[target]
    elif target not in channel.list and sign == '+':
        channel.list[target] = {'by': event('mask'), 'date': int(time.time())}
add_chan_trigger('+', trigger_ban_list)
add_chan_trigger('-', trigger_ban_list)


################################# list ######################################

# bans

pr = []
@handler(rpl(367, '!{target} !{mask} !{by} !{date}'))
def channel_bans(irc, ev):
    channel = ev('target')
    pr_id = ('%s/%s' % (irc.servname, channel)).lower()

    channel = irc.request.get_chan(channel)
    if channel is None:  # wtf
        return True

    if not pr_id in pr:
        pr.append(pr_id)
        channel.list.clear()

    channel.list[ev('mask').lower()] = {'by': ev('by'), 'date': int(ev('date'))}


@handler(rpl(368, '!{target} :?.*'))
def channel_bans_end(irc, ev):
    pr.remove(('%s/%s' % (irc.servname, ev('target'))).lower())