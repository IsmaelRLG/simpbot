# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)
#
# Simpcoins! inspired by buttcoins
#---------------------------------
from __future__ import unicode_literals

import time
import random
import simpbot
import hashlib

from simpbot.bottools.irc import color
from datetime import datetime as d
from . import config
from .database import User, Dealings
module = simpbot.get_module(sys=True)
loader = module.loader()
package = 'extra.simpcoins'
usermap = {}


def on_load():
    for usr in User.select():
        add_user(usr)


def add_user(usr):
    usermap[usr.id] = usr


def on_database(vars):
    irc = vars['self'].irc
    args = vars['watchdog'][1]
    network = irc.servname
    account = vars['user'].account
    target = vars['target']
    locale = simpbot.localedata.get(vars['lang'], package)

    if get_account(account, network) is None:
        if not 'ninja' in args:
            irc.error(target, locale['unregistered'])
        return True


def getid(account, network):
    return hashlib.md5('%s %s' % (account.lower(), network.lower())).hexdigest()


def transference(sender, receiver, amount):
    if not sender.decrease is False:
        if sender.coins < amount:
            return
        else:
            sender.coins -= amount
    receiver.coins += amount

    tr = Dealings.insert(id=hashlib.md5(str(int(time.time()))).hexdigest()[:8],
        sender=sender.id, receiver=receiver.id,
        amount=amount, date=d.utcnow())
    tr.execute()
    receiver.save()
    sender.save()


def open_account(account, network, decrease=True):
    usr = User.insert(id = getid(account, network),
    username = account,
    network = network,
    lines = 1,
    coins = config.default_coins,
    decrease = decrease,
    c_block = '',
    levelup = config.init_level,
    chances = config.default_chances)
    usr.execute()
    return get_account(account, network)


def get_account(account, network):
    if getid(account, network) in usermap:
        return usermap[getid(account, network)]
    else:
        try:
            usr = User.get(User.id == getid(account, network))
        except User.DoesNotExist:
            return
        else:
            add_user(usr)
            return usr


@loader('coin-handler', None,
    need=[
        'only:channel,ninja',
        'requires nickserv:ninja',
        'registered user:ninja',
        (on_database, 'ninja')])
def coins(irc, ev, result, target, channel, _, locale):
    network = irc.servname.lower()
    message = ev.group('message')

    usr = get_account(_['user'].account, network)
    if len(message) < config.min_len or usr is None:
        return

    usr.lines += 1
    if usr.lines > usr.levelup:
        usr.levelup += ((config.p_increase * usr.levelup) / 100)
        usr.chances += 1

    for chance in range(usr.chances):
        char = random.choice(config.full_block)
        if char in usr.c_block:
            continue
        else:
            usr.c_block += char
            break

    if len(usr.c_block) == len(config.full_block):
        bot = get_account(config.bot_account, network)
        if bot is None:
            bot = open_account(config.bot_account, network, False)
        transference(bot, usr, config.default_ecoins)
        usr.c_block = ''
    usr.save()


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

    usr = get_account(_['user'].account, irc.servname)
    if usr is None:
        if not action in ('create',):
            return irc.error(target, _(locale['unregistered']))

    if action in ('b', 'balance'):
        if _['arguments'] and _['arguments'].split()[0] != '':
            tar = get_account(_['arguments'].split()[0], irc.servname)
            if tar is None:
                irc.error(target, _(locale['unregistered user'], user=tar))
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

        return irc.msg(target, _(locale['balance'], usr=usr, c=c, p=p))
    elif action in ('tr', 'transfer'):
        args = _['arguments'].split()
        try:
            receiver = args[0]
            amount = args[1]
        except IndexError:
            return irc.error(target, _(locale['missing arguments']))

        if amount.isdigit():
            amount = int(amount)
        else:
            return irc.error(target, _(locale['invalid amount']))

        if usr.username.lower() == receiver.lower():
            return irc.error(target, locale['you can not autotransfer'])

        tar = get_account(receiver, irc.servname)
        if tar is None:
            return irc.error(target, _(locale['unregistered user'], user=tar))

        if amount > usr.coins and not usr.decrease:
            return irc.error(target, locale['insufficient balance'])

        transference(usr, tar, amount)
        irc.msg(target, _(locale['coins transferred'], f=usr, t=tar, a=amount))
    elif action in ('create',):
        if usr is not None:
            return irc.error(target, locale['already account created'])
        open_account(_['user'].account, irc.servname)
        irc.msg(target, _(locale['account created']))
    else:
        irc.msg(target, _(locale['usage']))
