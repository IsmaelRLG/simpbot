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
# set lang                              si
# set commands                          no
# join-msg                              no
# kick                                  si
# ban                                   si
# unban                                 si
# quiet                                 si
# unquiet                               si
# join                                  si
# part                                  si
# invite                                si
# cmode                                 no ~
# op                                    si
# deop                                  si
# voice                                 si
# devoice                               si
# say / msg                             si
# topic                                 no
#---------- varian en la red usada-------------
# remove                                no
# semi-op / half-op (hop)               no
# dsemi-op (dhop)                       no


import re

import simpbot
from simpbot import mode
from simpbot.bottools.irc import valid_mask
from simpbot.bottools.irc import parse_mask
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
        irc.join(channel.channel)
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
        code = irc.dbstore.get_request('chan', channel)[0]
        irc.verbose('request', _(locale['channel request'], code=code))
        irc.notice(target, _(locale['request sent']))
    elif irc.dbstore.chanregister == 'deny':
        irc.error(target, locale['registration disabled'])


@loader('lang channel',
    regex={'private': 'lang channel!{chan_name}? !{lang}',
        'channel': 'lang channel !{lang}'},
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:F'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax lang channel',
        'help': 'help lang channel'})
def lang_channel(irc, ev, result, target, channel, _, locale):
    lang = _['lang'].upper()
    if not lang in simpbot.localedata.simplocales.fullsupport():
        return irc.error(target, _(locale['invalid lang']))
    irc.dbstore.get_chan(channel).set_lang(lang)
    irc.dbstore.save()


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
    chan = channel
    if len(code) != 32 or not irc.dbstore.has_drop('chan', chan) or \
    irc.dbstore.get_hashdrop(_['chan_name']) != code:
        irc.error(user.nick, locale['invalid code'])
        return
    irc.dbstore.del_drop('chan', chan)
    irc.dbstore.drop_chan(chan)
    irc.notice(user.nick, _(locale['channel dropped']))
    irc.verbose('drop channel', _(locale['verbose: channel dropped']))


@loader('flags',
    regex={
        'private': 'flags {1,}!{chan_name} {1,}(?P<fg_type>list|!{target} {1,}!{flags})',
        'channel': 'flags {1,}(?P<fg_type>list|!{target} {1,}!{flags})'},
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:f'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax flags',
        'help': 'help flags'})
def flags(irc, ev, result, target, channel, _, locale):
    channel = irc.dbstore.get_chan(channel)
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
        diff[1] = '---'

    if diff[0] is None:
        diff[0] = '---'
    _['diff'] = diff
    msg = _('\2{target}\2: (\2{diff[0]}\2)  ->   (\2{diff[1]}\2)')
    irc.notice(target, locale['flags changed to'] % msg)
    if target.lower() != channel.channel and channel.verbose:
        irc.notice(target, _(locale['changed by'], ch_flags=msg))


@loader('founder', 'founder!{chan_name}? (?P<switch>add|del) !{account}',
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
    channel = irc.dbstore.get_chan(channel)
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


@loader('template', 'template!{chan_name}? (list|!{template} !{flags})',
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
    channel = irc.dbstore.get_chan(channel)
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
###############################################################################
###############################################################################
###############################################################################
###############################################################################


@loader('join', 'join {1,}!{chan_name}!{key}+?',
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:chan_name',
        'flags:f'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax join',
        'help': 'help join'})
def join(irc, ev, result, target, channel, _, locale):
    irc.join(channel, '' if not _['key'] else _['key'])


@loader('part',
    regex={
        'private': 'part {1,}!{chan_name}!{msg}+?',
        'channel': 'part !{msg}+?'},

    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:f'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax part',
        'help': 'help part'})
def part(irc, ev, result, target, channel, _, locale):
    msg = 'SimpBot v' + simpbot.__version__ if not _['msg'] else _['msg']
    irc.part(channel, msg)


def parse(irc, maxgroup, targets, channel, _, i18n):
    groups = []
    nicks = []

    def append(user, group):
        if user.nick.lower() in nicks:
            return
        if len(group) >= maxgroup:
            group = []
            groups.append(group)

        nicks.append(user.nick.lower())
        group.append(user.nick.lower())
        return group

    channel = irc.request.get_chan(channel)
    targets = targets if isinstance(targets, list) else targets.strip().split()
    for target in targets:
        try:
            group = groups.pop()
        except IndexError:
            group = []
        finally:
            groups.append(group)

        if valid_mask(target):
            mask = re.compile(parse_mask(target), re.IGNORECASE)
            for user in channel.users:
                if not mask.match(user.mask):
                    continue
                group = append(user, group)
        elif re.match('\$a:.+', target):
            account = target.split(':', 1)[1].lower()
            for user in channel.users:
                if not user.account or user.account.lower() != account:
                    continue
                group = append(user, group)
        else:
            for user in channel.users:
                if user.nick.lower() == target.lower():
                    append(user, group)
                    break
            else:
                irc.error(_['target'], _(i18n['no such nick'], nick=target))
    return groups


@loader('kick',
    regex={
        'private': 'k(ick)? {1,}!{chan_name} {1,}!{k_target}!{msg>}+?',
        'channel': 'k(ick)? {1,}!{k_target}!{msg}+?'},
    alias=('k', 'kick'),
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:k',
        'channel_status:o,h'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax kick',
        'help': 'help kick'})
def kick(irc, ev, result, target, channel, _, locale):
    usr = _['user']
    _['kicker'] = usr.account if usr.account else usr.nick
    if _['msg'] and not _['msg'].isspace():
        msg = '%s (%s)' % (_['msg'].rstrip(), _(locale['kicked by']))
    else:
        msg = _(locale['kicked by'])

    for gro in parse(irc, 100, _['k_target'], channel, _, locale):
        for victim in gro:
            if victim == irc.nickname.lower():
                continue
            irc.kick(channel, victim, msg)


@loader('op',
    regex={'channel': '(op( {1,}(?P<targets>.*))?)$',
        'private': 'op {1,}(?P<chan_name>[^ ]+)( {1,}(?P<targets>.*))?'},

    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:o',
        'channel_status:o'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax op',
        'help': 'help op'})
def op(irc, ev, result, target, channel, _, locale):
    targets = _['targets'].strip().split()
    if len(targets) == 0:
        targets.append(_['user'].nick)
    for gro in parse(irc, irc.features.modes, targets, channel, _, locale):
        irc.mode(channel, '+%s %s' % (len(gro) * 'o', ' '.join(gro)))


@loader('deop',
    regex={'channel': '(deop( {1,}(?P<targets>.*))?)$',
        'private': 'deop {1,}(?P<chan_name>[^ ]+)( {1,}(?P<targets>.*))?'},

    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:O',
        'channel_status:o'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax deop',
        'help': 'help deop'})
def deop(irc, ev, result, target, channel, _, locale):
    targets = _['targets'].strip().split()
    if len(targets) == 0:
        targets.append(_['user'].nick)
    for gro in parse(irc, irc.features.modes, targets, channel, _, locale):
        irc.mode(channel, '-%s %s' % (len(gro) * 'o', ' '.join(gro)))


@loader('voice',
    regex={'channel': '(v(oice)?( {1,}(?P<targets>.*))?)$',
        'private': 'v(oice)? (?P<chan_name>[^ ]+)( {1,}(?P<targets>.*))?'},
    alias=('v', 'voice'),
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:v',
        'channel_status:o,h'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax voice',
        'help': 'help voice'})
def voice(irc, ev, result, target, channel, _, locale):
    targets = _['targets'].strip().split()
    if len(targets) == 0:
        targets.append(_['user'].nick)
    for gro in parse(irc, irc.features.modes, targets, channel, _, locale):
        irc.mode(channel, '+%s %s' % (len(gro) * 'v', ' '.join(gro)))


@loader('devoice',
    regex={'channel': '(de?v(oice)?( {1,}(?P<targets>.*))?)$',
    'private': 'de?v(oice)? {1,}(?P<chan_name>[^ ]+)( {1,}(?P<targets>.*))?'},
    alias=('dv', 'devoice'),
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:v',
        'channel_status:o,h'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax devoice',
        'help': 'help devoice'})
def devoice(irc, ev, result, target, channel, _, locale):
    targets = _['targets'].strip().split()
    if len(targets) == 0:
        targets.append(_['user'].nick)
    for gro in parse(irc, irc.features.modes, targets, channel, _, locale):
        irc.mode(channel, '-%s %s' % (len(gro) * 'v', ' '.join(gro)))


@loader('quiet',
    regex={'channel': 'q(uiet)? {1,}!{q_target}',
        'private': 'q(uiet)? {1,}!{chan_name} {1,}!{q_target}'},
    alias=('q', 'quiet'),
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:b',
        'channel_status:o,h'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax quiet',
        'help': 'help quiet'})
def quiet(irc, ev, result, target, channel, _, locale):
    channel = irc.request.get_chan(channel)
    quiettype = '*!*@{user.host}'
    qtarget = _['q_target']

    if valid_mask(qtarget):
        irc.mode(channel.channel_name, '+q ' + qtarget)

    elif re.match('\$a:.+', qtarget):
        #--------------------#
        # Advertencia!       #
        #--------------------#
        # Solo para Freenode #
        # se debe añadir la  #
        # compatibilidad con #
        # otros ircd         #
        #--------------------#
        irc.mode(channel.channel_name, '+q ' + qtarget)

    else:
        if not irc.request.has_user(qtarget):
            irc.request.user(qtarget)
        user = irc.request.get_user(qtarget)

        if not user:
            return irc.error(target, _(locale['no such nick'], nick=qtarget))
        irc.mode(channel.channel_name, '+q ' + quiettype.format(user=user))


@loader('unquiet',
    regex={'channel': 'un?q(uiet)? {1,}!{q_target}',
        'private': 'un?q(uiet)? {1,}!{chan_name} {1,}!{q_target}'},
    alias=('uq', 'unquiet'),
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:B',
        'channel_status:o,h'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax unquiet',
        'help': 'help unquiet'})
def unquiet(irc, ev, result, target, channel, _, locale):
    channel = irc.request.get_chan(channel)
    quiettype = '*!*@{user.host}'
    qtarget = _['q_target']

    if valid_mask(qtarget):
        irc.mode(channel.channel_name, '-q ' + qtarget)

    elif re.match('\$a:.+', qtarget):
        #--------------------#
        # Advertencia!       #
        #--------------------#
        # Solo para Freenode #
        # se debe añadir la  #
        # compatibilidad con #
        # otros ircd         #
        #--------------------#
        irc.mode(channel.channel_name, '-q ' + qtarget)

    else:
        if not irc.request.has_user(qtarget):
            irc.request.user(qtarget)
        user = irc.request.get_user(qtarget)

        if not user:
            return irc.error(target, _(locale['no such nick'], nick=qtarget))
        irc.mode(channel.channel_name, '-q ' + quiettype.format(user=user))


@loader('ban',
    regex={'channel': 'b(an)? {1,}!{b_target}!{msg}+?',
        'private': 'b(an)? {1,}!{chan_name} {1,}!{b_target}!{msg}+?'},
    alias=('b', 'ban'),
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:b',
        'channel_status:o,h'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax ban',
        'help': 'help ban'})
def ban(irc, ev, result, target, channel, _, locale):
    channel = irc.request.get_chan(channel)
    bantype = '*!*@{user.host}'
    btarget = _['b_target'].strip()

    usr = _['user']
    _['kicker'] = usr.account if usr.account else usr.nick
    if _['msg'] and not _['msg'].isspace():
        msg = '%s (%s)' % (_['msg'].rstrip(), _(locale['kicked by']))
    else:
        msg = _(locale['kicked by'])

    if valid_mask(btarget):
        irc.mode(channel.channel_name, '+b ' + btarget)

    elif re.match('\$a:.+', btarget):
        #--------------------#
        # Advertencia!       #
        #--------------------#
        # Solo para Freenode #
        # se debe añadir la  #
        # compatibilidad con #
        # otros ircd         #
        #--------------------#
        irc.mode(channel.channel_name, '+b ' + btarget)

        for gro in parse(irc, 100, _['b_target'], channel, _, locale):
            for victim in gro:
                if victim == irc.nickname.lower():
                    continue
                irc.kick(channel, victim, msg)
    else:
        if not irc.request.has_user(btarget):
            irc.request.user(btarget)
        user = irc.request.get_user(btarget)

        if not user:
            return irc.error(target, _(locale['no such nick'], nick=btarget))

        irc.mode(channel.channel_name, '+b ' + bantype.format(user=user))
        for usr in channel.users:
            if usr.host == user.host:
                irc.kick(channel.channel_name, usr.nick, msg)


@loader('unban',
    regex={'channel': 'un?b(an)? {1,}!{b_target}',
        'private': 'un?b(an)? {1,}!{chan_name} {1,}!{b_target}'},
    alias=('ub', 'unban'),
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:B',
        'channel_status:o,h'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax unban',
        'help': 'help unban'})
def unban(irc, ev, result, target, channel, _, locale):
    channel = irc.request.get_chan(channel)
    bantype = '*!*@{user.host}'
    btarget = _['b_target']

    if valid_mask(btarget):
        irc.mode(channel.channel_name, '-b ' + btarget)

    elif re.match('\$a:.+', btarget):
        #--------------------#
        # Advertencia!       #
        #--------------------#
        # Solo para Freenode #
        # se debe añadir la  #
        # compatibilidad con #
        # otros ircd         #
        #--------------------#
        irc.mode(channel.channel_name, '-b ' + btarget)

    else:
        if not irc.request.has_user(btarget):
            irc.request.user(btarget)
        user = irc.request.get_user(btarget)

        if not user:
            return irc.error(target, _(locale['no such nick'], nick=btarget))
        irc.mode(channel.channel_name, '-b ' + bantype.format(user=user))


@loader('say',
    regex={'channel': '(say|msg) !{msg}+',
        'private': '(say|msg) {1,}!{chan_name} !{msg}+'},
    alias=('say', 'msg'),
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:o'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax say',
        'help': 'help say'})
def say(irc, ev, result, target, channel, _, locale):
    irc.privmsg(channel, _['msg'])


@loader('invite',
    regex={'channel': 'invite !{targets}+',
        'private': 'invite !{chan_name}!{targets}+?'},
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:private=chan_name,channel=non-channel',
        'flags:i'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.channel',
        'syntax': 'syntax invite',
        'help': 'help invite'})
def invite(irc, ev, result, target, channel, _, locale):
    targets = _['targets'].strip().split()
    if len(targets) == 0:
        targets.append(_['user'].nick)
    for nick in targets:
        irc.invite(nick, channel)