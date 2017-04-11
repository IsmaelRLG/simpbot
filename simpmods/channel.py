# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)
# Lista de tareas: comandos por agregar
###############################################
# COMANDO                             # AÑADIDO
#----------------------------------------------
# register                              si
# drop                                  si
# confirm drop                          si
# flags                                 si
# founder                               si
# template                              si
# set lang                              no
# set commands                          no
# join-msg                              no
# kick                                  no
# ban                                   no
# unban                                 no
# quiet                                 no
# unquiet                               no
# join                                  no
# part                                  no
# invite                                no
# cmode                                 no
# op                                    no
# deop                                  no
# voice                                 no
# devoice                               no
# say / msg                             no
#---------- varian en la red usada-------------
# remove                                no
# semi-op (sop)                         no
# dsemi-op (dsop)                       no
# half-op (hop)                         no

import simpbot
from simpbot import mode
from simpbot.bottools.irc import valid_mask
module = simpbot.get_module(sys=True)
loader = module.loader()


@loader('register channel', 'register channel !{chan_name}',
    need=[
        'requires nickserv',
        'registered user',
        'unregistered chan:chan_name'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax register channel',
        'help': 'help register channel'})
def register(irc, ev, result, target, channel, _, locale):
    channel = _['chan_name']
    user = _['user']

    def check_max():
        if irc.dbstore.max_channels == 0:
            return True
        total = len(irc.dbstore.store_request['chan'])
        total += irc.dbstore.total_chan()
        if total < irc.dbstore.max_channels:
            return True
        elif (total + 1) == irc.dbstore.max_channels:
            irc.verbose('request', locale['max channels'])
        irc.error(target, locale['registration disabled'])
        return False

    if irc.dbstore.chanregister == 'allow':
        if not check_max():
            return
        irc.dbstore.register_chan(channel)
        channel = irc.dbstore.get_chan(channel)
        channel.set_flags(irc.dbstore.get_user(user.account), 'founder')
        irc.dbstore.save()
        msg = _(locale['channel registered'])
        irc.verbose('new channel', msg)
        irc.notice(target, msg)
        irc.join(channel)
    elif irc.dbstore.chanregister == 'request':
        if irc.dbstore.has_request('chan', (channel, user.account)):
            request = irc.dbstore.get_request('chan', channel)
            if request[1] == user.account.lower():
                irc.error(target, locale['you already requested this'])
                return
            irc.error(target, _(locale['already requested'], usr=request[1]))
            return

        if not check_max():
            return
        irc.dbstore.request('chan', (channel, user.account))
        code = irc.dbstore.get_request(channel)[0]
        irc.verbose('request', _(locale['channel request'], code=code))
        irc.notice(target, _(locale['request sent']))
    elif irc.dbstore.chanregister == 'deny':
        irc.error(target, locale['registration disabled'])


@loader('drop channel', 'drop channel !{chan_name}',
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:chan_name',
        'flags:F'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax drop channel',
        'help': 'help drop channel'})
def drop(irc, ev, result, target, channel, _, locale):
    if irc.dbstore.has_drop('chan', _['chan_name']):
        _['code'] = irc.dbstore.get_hashdrop(_['chan_name'])
    else:
        _['code'] = irc.dbstore.drop('chan', _['chan_name'])
    irc.notice(_['user'].nick, _(locale['confirm drop']))


@loader('confirm drop:chan', 'confirm drop:chan !{chan_name} !{code}',
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:chan_name',
        'flags:F'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax confirm drop',
        'help': 'help confirm drop'})
def confirm(irc, ev, result, target, channel, _, locale):
    user = _['user']
    code = _['code']
    chan = _['chan_name']
    if len(code) != 32 or not irc.dbstore.has_drop('chan', chan) or \
    irc.dbstore.get_hashdrop(_['chan_name']) != code:
        irc.error(user.nick, locale['invalid code'])
        return
    irc.dbstore.del_drop('chan', chan)
    irc.dbstore.drop_chan(chan)
    irc.notice(user.nick, _(locale['channel dropped']))
    irc.verbose('drop channel', _(locale['verbose: channel dropped']))


@loader('flags', 'flags !{chan_name} (?P<fg_type>list|!{target} !{flags})',
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:chan_name',
        'flags:f'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax flags',
        'help': 'help flags'})
def flags(irc, ev, result, target, channel, _, locale):
    channel = irc.dbstore.get_chan(_['chan_name'])
    account = _['target']
    user = _['user']

    if _['fg_type'] == 'list':
        irc.msg(target, _(locale['flags list']))
        base_row = '%s %-{L_NICK_COL}s  %s'
        nick_col = locale['nick column']
        flag_col = locale['flag column']
        SEP = '-'
        N_L = 3
        L_FLAG_COL = len(flag_col)
        L_NICK_COL = irc.features.nicklen
        if len(nick_col) > irc.features.nicklen:
            L_NICK_COL = len(nick_col)
        base_row = base_row.format(L_NICK_COL=L_NICK_COL)
        div_row = '%s %s  %s' % (SEP * N_L, SEP * L_NICK_COL, SEP * L_FLAG_COL)
        irc.msg(target, base_row % (' ' * N_L, nick_col, flag_col))
        irc.msg(target, div_row)
        flag_n = 0

        for name, flag in channel.flags.items():
            flag_n += 1
            if hasattr(name, 'username'):
                name = name.username
            elif isinstance(name, tuple):
                name = name[1]
            irc.msg(target, base_row % (str(flag_n).zfill(N_L), name, flag))
        else:
            if flag_n == 0:
                return
        irc.msg(target, div_row)
        return

    # El usuario a modificar los flags
    if not valid_mask(account):
        account = irc.dbstore.get_user(account)
        if not account:
            return irc.error(target, _(locale['invalid mask']))

    # El usuario que los modifica
    account_2 = irc.dbstore.get_user(user.account)

    ddel = 'F'
    dadd = 'F'

    if hasattr(account, 'username'):
        _['target'] = account.username
        if account_2.username.lower() != account.username.lower():
            if channel.has_flags(account):
                if 'F' in channel.get_flags(account):
                    ddel += 'f'

    diff = channel.set_flags(account, _['flags'], dadd, ddel)
    irc.dbstore.save()
    if not diff:
        return irc.error(target, locale['could not be set flags'])

    if diff[0] == diff[1]:
        irc.notice(target, _(locale['flags unchanged']))
        return

    diff = list(diff)
    if diff[1] is None:
        diff[1] = '-'

    if diff[0] is None:
        diff[0] = '---'
    _['diff'] = diff
    msg = _('\2{target}\2: (\2{diff[0]}\2)  ->   (\2{diff[1]}\2)')
    irc.notice(target, locale['flags changed to'] % msg)
    if target.lower() != channel.channel and channel.verbose:
        irc.notice(target, _(locale['changed by'], ch_flags=msg))


@loader('founder', 'founder !{chan_name} (?P<switch>add|del) !{account}',
    need=[
        'requires nickserv',
        'registered user',
        'registered user:account',
        'registered chan:chan_name',
        'flags:F'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax founder',
        'help': 'help founder'})
def founder(irc, ev, result, target, channel, _, locale):
    channel = irc.dbstore.get_chan(_['chan_name'])
    account = irc.dbstore.get_user(_['account'])
    switch = _['switch']
    if switch == 'add':
        diff = channel.set_flags(account, '+F')
    elif switch == 'del':
        diff = channel.set_flags(account, '-F')

    if not diff or diff[0] == diff[1]:
        return irc.error(target, locale['could not be set founder'])

    irc.dbstore.save()
    diff = list(diff)
    if diff[1] is None:
        diff[1] = '---'

    if diff[0] is None:
        diff[0] = '---'
    _['diff'] = diff
    msg = _('\2{account}\2: (\2{diff[0]}\2)  ->   (\2{diff[1]}\2)')
    irc.notice(target, locale['flags changed to'] % msg)
    if target.lower() != channel.channel and channel.verbose:
        irc.notice(target, _(locale['changed by'], ch_flags=msg))


@loader('template', 'template !{chan_name} (list|!{template} !{flags})',
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:chan_name',
        'flags:s'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax template',
        'help': 'help template'})
def template(irc, ev, result, target, channel, _, locale):
    channel = irc.dbstore.get_chan(_['chan_name'])
    template_name = _['template'].lower()
    max_length = 15
    if template_name == '' and _['flags'] == '':
        irc.notice(target, _(locale['template list']))
        base_row = '%s %-{L_NAME_COL}s  %s'
        name_col = locale['name column']
        flag_col = locale['flag column']
        SEP = '-'
        N_L = 3
        L_FLAG_COL = len(flag_col)
        L_NAME_COL = max_length if len(name_col) < max_length else len(name_col)

        base_row = base_row.format(L_NAME_COL=L_NAME_COL)
        div_row = '%s %s  %s' % (SEP * N_L, SEP * L_NAME_COL, SEP * L_FLAG_COL)
        irc.msg(target, base_row % (' ' * N_L, name_col, flag_col))
        irc.msg(target, div_row)
        flag_n = 0
        for template, flag in channel.template.items():
            flag_n += 1
            irc.msg(target, base_row % (str(flag_n).zfill(N_L), template, flag))
        else:
            if flag_n == 0:
                return
        return irc.msg(target, div_row)

    if len(template_name) > max_length:
        return irc.error(target, locale['name too long'])

    if not template_name in channel.template:
        channel.template[template_name] = ''

    for sign, ch, null in mode._parse_modes(_['flags'], only='FOVbfiklmorstv'):
        value = channel.template[template_name]
        if sign == '+':
            if ch in value:
                continue
            value += ch
        elif sign == '-':
            if not ch in value:
                continue
            value = value.replace(ch, '')
        channel.template[template_name] = value

    value = [n for n in channel.template[template_name]]
    value.sort()
    value = ''.join(value)
    channel.template[template_name] = value

    if len(channel.template[template_name]) == 0 and template_name != 'clear':
        del channel.template[template_name]
        irc.dbstore.save()
        irc.notice(target, _(locale['template deleted']))
    else:
        irc.dbstore.save()
        _['flags'] = channel.template[template_name]
        if len(_['flags']) == 0:
            _['flags'] = '---'
        irc.notice(target, _(locale['template edited']))

