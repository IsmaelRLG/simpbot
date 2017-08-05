# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import simpbot
module = simpbot.get_module(sys=True)
loader = module.loader()


@loader('register user', 'register user',
    need=[
        'requires nickserv',
        'unregistered user'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.user',
        'syntax': 'syntax register',
        'help': 'help register'})
def register(irc, ev, result, target, channel, _, locale):
    user = _['user']

    def check_max():
        ok = True
        no = False
        if irc.dbstore.max_users == 0:
            return ok
        total = len(irc.dbstore.store_request['chan'])
        total += irc.dbstore.total_user()
        if total < irc.dbstore.max_users:
            return ok
        elif (total + 1) == irc.dbstore.max_users:
            irc.verbose('request', locale['max users'])
        irc.error(target, locale['registration disabled'])
        return no

    if irc.dbstore.userregister == 'allow':
        if not check_max():
            return
        irc.dbstore.register_user(user.account)
        irc.notice(target, _(locale['user registered']))
        irc.verbose('new user', _(locale['verbose: user registered']))
    elif irc.dbstore.userregister == 'request':
        if irc.dbstore.has_request('user', user.account):
            irc.error(target, locale['you already requested this'])
            return
        if not check_max():
            return
        irc.dbstore.request('user', user.account)
        code = irc.dbstore.get_request(user.account)[0]
        irc.verbose('request', _(locale['user request'], code=code))
        irc.notice(target, _(locale['request sent']))
    elif irc.dbstore.userregister == 'deny':
        irc.error(target, locale['registration disabled'])


@loader('drop user', 'drop user',
    need=[
        'requires nickserv',
        'registered user'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.user',
        'syntax': 'syntax drop',
        'help': 'help drop'})
def drop(irc, ev, result, target, channel, _, locale):
    user = _['user']
    if irc.dbstore.has_drop('user', user.account):
        _['hash'] = irc.dbstore.get_hash(user.account)
    else:
        _['hash'] = irc.dbstore.drop('user', user.account)
    irc.notice(user.nick, _(locale['confirm drop']))


@loader('confirm drop:user', 'confirm drop:user !{code}',
    syntax="",
    need=[
        'requires nickserv',
        'registered user'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.user',
        'syntax': 'syntax confirm drop',
        'help': 'help confirm drop'})
def confirm(irc, ev, result, target, channel, _, locale):
    user = _['user']
    code = _['code']
    if len(code) != 32 or not irc.dbstore.has_drop('user', user.account) or \
    irc.dbstore.get_hash(user.account) != code:
        irc.error(user.nick, locale['invalid code'])
        return
    irc.dbstore.del_drop('user', user.account)
    irc.dbstore.drop_user(user.account)
    irc.notice(user.nick, _(locale['user dropped']))
    irc.verbose('drop user', _(locale['verbose: user droppped']))