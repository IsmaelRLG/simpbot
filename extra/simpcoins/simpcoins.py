# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)
#
# Simpcoins! inspired by buttcoins
#---------------------------------
from __future__ import unicode_literals

import simpbot
import prettytable

from simpbot.bottools.irc import color
from . import config
from . import tools
from .database import User, Dealings
module = simpbot.get_module(sys=True)
loader = module.loader()
package = 'extra.simpcoins'


def gentable(columns):
    table = prettytable.PrettyTable(columns, **config.table_format)
    table._set_align('l')
    return table


def on_database(vars):
    irc = vars['self'].irc
    args = vars['watchdog'][1]
    target = vars['target']
    locale = simpbot.localedata.get(vars['lang'], package)
    usr = tools.dispatch(irc.servname)[vars['user'].account]
    if usr is None:
        if not 'ninja' in args:
            irc.error(target, locale['unregistered'])
        return True
    elif 'manager' in args and not usr.manager:
        if not 'ninja' in args:
            irc.error(target, locale['only managers'])
        return True


@loader('coin-handler', None,
    need=[
        'only:channel,ninja',
        'requires nickserv:ninja',
        'registered user:ninja',
        (on_database, 'ninja')])
def coins(irc, ev, result, target, channel, _, locale):
    bank = tools.dispatch(irc.servname)
    usr = bank.get(_['user'].account)

    if len(ev.group('message')) < config.min_len or usr is None or usr.locked:
        return
    bank.increase_lines(usr)


@loader('simp', 'simp(coins)? !{action}!{arguments}+?',
    need=[
        #'only:channel,ninja',
        'requires nickserv',
        'registered user',
        #(on_database, ['aperture'])
        ],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': package,
        'syntax': 'syntax simp',
        'help': 'help simp'})
def simp(irc, ev, result, target, channel, _, locale):
    action = _['action']
    account = _['user'].account
    bank = tools.dispatch(irc.servname)

    usr = bank.get(account)
    if usr is None and not action in ('create',):
        return irc.error(target, _(locale['unregistered']))

    if action in ('b', 'balance'):
        if _['arguments'] and _['arguments'].split()[0] != '':
            name = _['arguments'].split()[0]
            tar = bank.get(name)
            if tar is None:
                irc.error(target, _(locale['unregistered user'], usr=name))
                return
            usr = tar

        c = round(len(usr.c_block) * 100.0 / len(config.full_block), 2)
        p = {0: color('%s', '04', bold=True) % locale['null'],
            1: color('%s', '13', bold=True) % locale['low'],
            2: color('%s', '01', bold=True) % locale['normal'],
            3: color('%s', '02', bold=True) % locale['good'],
            4: color('%s', '07', bold=True) % locale['hight'],
            5: color('%s', '03', bold=True) % locale['excellent']}
        p = p[5 if usr.chances > 5 else usr.chances]
        a = usr.coins if usr.decrease else '---'
        return irc.msg(target, _(locale['balance'], usr=usr, c=c, p=p, a=a))
    elif action in ('tr', 'transfer'):
        args = _['arguments'].split()
        try:
            name = args[0]
            a = args[1]
        except IndexError:
            return irc.error(target, _(locale['missing arguments']))

        if a.isdigit() and int(a) != 0:
            a = int(a)
        else:
            return irc.error(target, _(locale['invalid amount']))

        if usr.username.lower() == name.lower():
            return irc.error(target, locale['you can not autotransfer'])

        tar = bank.get(name)
        if tar is None:
            return irc.error(target, _(locale['unregistered user'], usr=name))

        if a > usr.coins and usr.decrease:
            return irc.error(target, locale['insufficient balance'])

        c = bank.transfer(usr, tar, a)
        irc.msg(target, _(locale['coins transferred'], f=usr, t=tar, a=a, c=c))

    elif action in ('create',):
        if usr is not None:
            return irc.error(target, locale['already account created'])
        bank.create(account)
        irc.msg(target, _(locale['account created']))
    elif action in ('h', 'history'):
        try:
            page = int(_['arguments'].split()[0])
        except:
            page = 1

        query = Dealings.select().where(
            (Dealings.to_user == usr) |
            (Dealings.from_user == usr))
        total = query.count()
        if total == 0:
            return irc.msg(target, locale['nothing to show'])

        pages = total / float(config.max_entries)
        pages = int(pages + 1) if pages.is_integer() else int(pages)

        if page > pages:
            return irc.error(target, locale['invalid page'])
        table = gentable([locale[c] for c in config.columns_name])

        for t in query.paginate(page, config.max_entries):
            row = [t.id]

            row.append(t.from_user.username)
            row.append(t.to_user.username)
            row.append(str(t.amount))

            # date column
            row.append(t.date.strftime(config.dateformat))
            table.add_row(row)

        irc.msg(_['user'].nick, table.get_string())
        irc.msg(_['user'].nick, _(locale['showing pages'], p=page, P=pages))

    elif action in ('check', 'chk'):
        args = _['arguments'].split()
        try:
            id = args[0]  # lint:ok
        except IndexError:
            return irc.error(target, _(locale['missing arguments']))

        try:
            t = Dealings.get(Dealings.id == id)
        except Dealings.DoesNotExist:
            return irc.error(target, locale['invalid id'])

        table = gentable([locale[c] for c in config.columns_name])
        row = [t.id]

        row.append(t.from_user.username)
        row.append(t.to_user.username)
        row.append(str(t.amount))

        row.append(t.date.strftime(config.dateformat))
        table.add_row(row)
        irc.msg(target, table.get_string())

    else:
        irc.msg(target, _(locale['usage']))


# Simp Bank manager
@loader('sbm', 'sbm !{action}!{arguments}+?',
    need=[
        #'only:channel,ninja',
        'requires nickserv',
        'registered user',
        (on_database, ['manager'])
        ],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': package,
        'syntax': 'syntax sbm',
        'help': 'help sbm'})
def sbm(irc, ev, result, target, channel, _, locale):
    action = _['action']
    account = _['user'].account
    bank = tools.dispatch(irc.servname)

    if action in ('clients', 'cl'):
        try:
            page = int(_['arguments'].split()[0])
        except:
            page = 1

        query = bank.usermap.values()
        total = len(bank.usermap)
        if total == 0:
            return irc.msg(target, locale['nothing to show'])

        pages = total / float(config.max_entries)
        pages = int(pages + 1) if pages.is_integer() else int(pages)
        if page > pages:
            return irc.error(target, locale['invalid page'])

        table = gentable([
            locale['column username'],
            locale['column balance'],
            locale['column date'],
            locale['column lastseen']])

        for usr in query[(page-1)*config.max_entries:page*config.max_entries]:
            table.add_row([usr.username, usr.coins,
            usr.join_date.strftime(config.dateformat),
            usr.last_seen.strftime(config.dateformat)])

        irc.msg(_['user'].nick, table.get_string())
        irc.msg(_['user'].nick, _(locale['showing pages'], p=page, P=pages))

    elif action in ('cheat', 'ch'):
        try:
            args = _['arguments'].split()
            name = args[0]
            switch = args[1].lower()
        except:
            return irc.error(target, _(locale['missing arguments']))

        usr = bank.get(name)
        if usr is None:
            return irc.error(target, _(locale['unregistered user'], usr=name))

        if not switch in ('on', 'off'):
            return irc.error(target, locale['invalid switch'])

        if switch == 'on':
            if usr.decrease:
                usr.decrease = False
                irc.msg(target, _(locale['cheat switched on'], usr=usr))
            else:
                return irc.error(target, locale['already switched'])
        elif switch == 'off':
            if not usr.decrease:
                usr.decrease = True
                irc.msg(target, _(locale['cheat switched off'], usr=usr))
            else:
                return irc.error(target, locale['already switched'])
        usr.save()

    elif action in ('reset',):
        try:
            name = _['arguments'].split()[0]
        except IndexError:
            return irc.error(target, _(locale['missing arguments']))

        usr = bank.get(name)
        if usr is None:
            return irc.error(target, _(locale['unregistered user'], usr=name))

        usr.locked = False
        usr.manager = False  # Manager of Simp Bank
        usr.lines = 1
        usr.coins = config.default_coins
        usr.decrease = True
        usr.c_block = ''  # current block
        usr.levelup = config.init_level  # lines needed to level up
        usr.chances = config.default_chances
        usr.backpack_size = config.default_bp_size
        usr.save()  # diabolic 3:D
        irc.msg(target, _(locale['account reset'], usr=usr))

    elif action in ('give',):
        try:
            args = _['arguments'].split()
            name = args[0]
            a = args[1]
        except:
            return irc.error(target, _(locale['missing arguments']))

        try:
            a = int(a)
        except ValueError:
            return irc.error(target, _(locale['invalid amount']))

        tar = bank.get(name)
        if tar is None:
            return irc.error(target, _(locale['unregistered user'], usr=name))

        usr = bank.get(account)
        c = bank.transfer(usr, tar, a, False)
        irc.msg(target, _(locale['coins transferred'], f=usr, t=tar, a=a, c=c))

    elif action in ('lock',):
        try:
            args = _['arguments'].split()
            name = args[0]
            switch = args[1].lower()
        except:
            return irc.error(target, _(locale['missing arguments']))

        usr = bank.get(name)
        if usr is None:
            return irc.error(target, _(locale['unregistered user'], usr=name))

        if not switch in ('on', 'off'):
            return irc.error(target, locale['invalid switch'])

        if switch == 'on':
            if not usr.locked:
                usr.locked = True
                irc.msg(target, _(locale['lock switched on'], usr=usr))
            else:
                return irc.error(target, locale['already switched'])
        elif switch == 'off':
            if usr.locked:
                usr.locked = False
                irc.msg(target, _(locale['lock switched off'], usr=usr))
            else:
                return irc.error(target, locale['already switched'])

        usr.save()

    elif action in ('h', 'history'):
        try:
            args = _['arguments'].split()
            name = args[0]
            try:
                page = int(args[1].lower())
            except:
                page = 1
        except:
            return irc.error(target, _(locale['missing arguments']))

        usr = bank.get(name)
        if usr is None:
            return irc.error(target, _(locale['unregistered user'], usr=name))

        query = Dealings.select().where(
            (Dealings.to_user == usr) |
            (Dealings.from_user == usr))

        total = query.count()
        if total == 0:
            return irc.msg(target, locale['nothing to show'])

        pages = total / float(config.max_entries)
        pages = int(pages + 1) if pages.is_integer() else int(pages)

        if page > pages:
            return irc.error(target, locale['invalid page'])
        table = gentable([locale[c] for c in config.columns_name])

        for t in query.paginate(page, config.max_entries):
            row = [t.id]

            row.append(t.from_user.username)
            row.append(t.to_user.username)
            row.append(str(t.amount))

            # date column
            row.append(t.date.strftime(config.dateformat))
            table.add_row(row)

        irc.msg(_['user'].nick, table.get_string())
        irc.msg(_['user'].nick, _(locale['showing pages'], p=page, P=pages))


@loader('set-sbm', 'set-sbm !{account} (?P<switch>on|off)',
    need=[
        'requires nickserv',
        'registered user',
        'admin:simple',
        (on_database, []),
        ],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': package,
        'syntax': 'syntax set-sbm',
        'help': 'help set-sbm'})
def set_sbm(irc, ev, result, target, channel, _, locale):
    name = _['account']
    usr = tools.dispatch(irc.servname).get(name)
    if usr is None:
        return irc.error(target, _(locale['unregistered user'], usr=name))

    usr.manager = _['switch'].lower() == 'on'
    usr.save()
    irc.msg(target, _(locale['manager switched'], usr=usr))


# Tengo flojera de programar, para despues:D
#@loader('store', 'store (?P<action>buy !{item_id}!{n}?|list!{page}?)',
#    need=[
#        #'only:channel,ninja',
#        'requires nickserv',
#        'registered user',
#        (on_database, [])],
#
#    i18n={
#        'loader': simpbot.localedata.simplocales,
#        'module': package,
#        'syntax': 'syntax simp',
#        'help': 'help simp'})
#def simp(irc, ev, result, target, channel, _, locale):
#    pass
