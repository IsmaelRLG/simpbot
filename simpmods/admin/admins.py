# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import simpbot
import random
import time
from simpbot import admins
from simpbot.bottools.irc import color
module = simpbot.get_module(sys=True)
loader = module.loader()
minlen = 4


def censore(text, per=50, sub='*'):
    text = [l for l in text]
    sublen = len(text) * float(per) / 100
    if not sublen.is_integer():
        sublen += 1
    subrang = list(range(len(text)))
    while sublen > 0:
        sublen -= 1
        index = random.choice(subrang)
        subrang.remove(index)
        text.insert(index, sub)
        text.pop(index + 1)
    return ''.join(text)


def checkpass(admin, password):
    if len(password) <= minlen or admin.checkpass(password):
        return False

    alpha = False
    digit = False
    space = False
    charsp = False
    for ch in password:
        if ch.isalpha() and not alpha:
            alpha = True
        elif ch.isdigit() and not digit:
            digit = True
        elif ch.isspace() and not space:
            space = True
        elif not ch.isalnum() and not charsp:
            charsp = True
    return alpha and digit and not space and charsp


@loader('auth', 'auth !{account} !{password}',
    need=[
        'requires nickserv',
        'registered user',
        'only:private'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.admin.admins',
        'syntax': 'auth syntax',
        'help': 'auth help'})
def auth(irc, ev, result, target, channel, _, locale):
    user = irc.dbstore.get_user(_['user'].account)
    account = _['account']
    password = _['password']

    def fail_login(extreason='', passwd=True):
        irc.error(target, locale['fail login'])
        if passwd:
            _['password'] = censore(password)
        else:
            _['password'] = '****'
        irc.verbose('fail login', _(locale['verbose: fail login']) +
        ', ' + extreason if extreason else extreason)
        # Colocar aquí el baneo

    if admins.has_admin(None, account):
        admin = admins.get_admin(None, account)
    elif admins.has_admin(irc.servname, account):
        admin = admins.get_admin(irc.servname, account)
    else:
        return fail_login()

    if not admin.checkpass(password):
        return fail_login()
    elif len(admin.account) > 0 and not user.username in admin.account:
        return fail_login(locale['ns account not allowed'], passwd=False)
    elif admin.has_maxlogin():
        return fail_login(locale['max of sessions reached'], passwd=False)

    if user.isadmin() and user.admin.logins > 0:
        user.admin.logins -= 1

    user.set_admin(str(admin), time.time())
    irc.dbstore.save()
    irc.notice(target, locale['login successful'])
    irc.verbose('login', _(locale['verbose: login successful']))


@loader('passwd', 'passwd !{old_passwd} !{new_passwd}+',
    need=[
        'requires nickserv',
        'registered user',
        'admin:update password',
        'only:private'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.admin.admins',
        'syntax': 'passwd syntax',
        'help': 'passwd help'})
def update_passwd(irc, ev, result, target, channel, _, locale):
    admin = irc.dbstore.get_user(_['user'].account).admin
    old_passwd = _['old_passwd']
    new_passwd = _['new_passwd']

    if not admin.checkpass(old_passwd) or not checkpass(admin, new_passwd):
        return irc.error(target, locale['invalid new password'])

    admin.update_password(new_passwd)

    _['admin_name'] = color(str(admin), 'b')
    irc.notice(target, _(locale['update password']))
    irc.verbose('update password', _(locale['verbose: update password']))


@loader('forcepasswd', 'forcepasswd !{admin} !{new_passwd}',
    need=[
        'requires nickserv',
        'registered user',
        'admin:update admin password',
        'only:private'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.admin.admins',
        'syntax': 'forcepasswd syntax',
        'help': 'forcepasswd help'})
def forcepasswd(irc, ev, result, target, channel, _, locale):
    account = _['admin']
    new_passwd = _['new_passwd']

    if admins.has_admin(None, account):
        admin = admins.get_admin(None, account)
    elif admins.has_admin(irc.servname, account):
        admin = admins.get_admin(irc.servname, account)
    else:
        return irc.notice(target, _(locale['invalid admin account']))

    if not checkpass(new_passwd):
        return irc.error(target, _(locale['invalid new password'], n=minlen))

    admin.update_password(new_passwd)
    _['admin_name'] = color(str(admin), 'b')
    irc.notice(target, _(locale['update password']))
    irc.verbose('update password', _(locale['verbose: force update password']))


@loader('logout', 'logout',
    syntax="logout",

    need=[
        'requires nickserv',
        'registered user',
        'admin'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.admin.admins',
        'help': 'logout help'})
def logout(irc, ev, result, target, channel, _, locale):
    user = irc.dbstore.get_user(_['user'].account)
    user.set_admin(None, None)
    irc.notice(target, locale['logout'])
    irc.verbose(target, _(locale['verbose']))


@loader('forcelogout', 'forcelogout !{account}',
    need=[
        'requires nickserv',
        'registered user',
        'admin:forcelogout',
        'registered user:account'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.admin.admins',
        'syntax': 'forcelogout syntax',
        'help': 'forcelogout help'})
def forcelogout(irc, ev, result, target, channel, _, locale):
    user = irc.dbstore.get_user(_['account'])
    user.set_admin(None, None)
    irc.notice(target, _(locale['forcelogout']))
    irc.verbose(target, _(locale['verbose: forcelogout']))


@loader('sessions', 'sessions',
    syntax="sessions",
    need=[
        'requires nickserv',
        'registered user',
        'admin:sessions',
        'only:private'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.admin.admins',
        'help': 'sessions help'})
def sessions(irc, ev, result, target, channel, _, locale):
    online = color('\356\210\246', 3) + ' - logged'
    offline = color('\356\210\246', 15) + ' - offline'
    dateform = '[{date.tm_year}/{date.tm_mon}/{date.tm_mday}]'
    dateform += '({date.tm_hour}:{date.tm_min}:{date.tm_sec})'
    for admin in simpbot.envvars.admins.values():
        if not admin.isglobal() and admin.network != irc.servname:
            continue
        if admin.logged():
            irc.notice(target, color(admin.user, 'b') + ' - ' + online)
            for user in irc.dbstore.admins_list():
                if not user.isadmin() or str(user.admin) != str(admin):
                    continue

                _['network'] = user.network
                _['ns'] = user.username
                _['date'] = time.localtime(user.logindate)
                _['since'] = _(dateform)
                if admin.timeout:
                    _['date'] = time.localtime(user.logindate + admin.timeout)
                    _['expire'] = _(dateform)
                else:
                    _['expire'] = '---'

                irc.notice(target, '   |-> ' + _(locale['sessions info']))
        else:
            irc.notice(target, color(admin.user, 'b') + ' - ' + offline)


@loader('admin add', 'admin add !{account} !{algth} !{hash} !{capab}+',
    need=[
        'requires nickserv',
        'registered user',
        'admin:superuser',
        'only:private'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.admin.admins',
        'syntax': 'admin add syntax',
        'help': 'admin add help'},
    record=':admins:')
def admin_add(irc, ev, result, target, channel, _, locale):
    network = irc.servname.lower()
    account = _['account'].lower()

    if admins.has_admin(network, account) or admins.has_admin(None, account):
        return irc.error(target, locale['duplicate admin'] % account)

    admins.add_admin(network, account, _['hash'], _['capabs'], save=True)
    if admins.has_admin(network, account):
        irc.notice(target, _(locale['admin added']))
    else:
        irc.notice(target, _(locale['cannot add admin']))


@loader('admin add', 'admin del !{account}',
    need=[
        'requires nickserv',
        'registered user',
        'admin:superuser',
        'only:private'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.admin.admins',
        'syntax': 'admin del syntax',
        'help': 'admin del help'},
    record=':admins:')
def admin_del(irc, ev, result, target, channel, _, locale):
    network = irc.servname.lower()
    account = _['account'].lower()

    if not admins.has_admin(network, account):
        return irc.error(target, locale['admin not found'] % account)

    admins.del_admin(network, account)
    if admins.has_admin(network, account):
        irc.notice(target, _(locale['admin deleted']))
    else:
        irc.notice(target, _(locale['cannot del admin']))


@loader('admin add', 'admin info !{account}',
    need=[
        'requires nickserv',
        'registered user',
        'admin:superuser',
        'only:private'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.admin.admins',
        'syntax': 'admin del syntax',
        'help': 'admin del help'},
    record=':admins:')
def admin_info(irc, ev, result, target, channel, _, locale):
    network = irc.servname.lower()
    account = _['account'].lower()

    if not admins.has_admin(network, account):
        return irc.error(target, locale['admin not found'] % account)

    adm = admins.get_admin(network, account)
    msg = lambda text: irc.notice(target, text)
    msg(_(locale['admin info']))
    msg(color('timeout', 'b') + ': %s' % adm.timeout)
    msg(color('maxlogins', 'b') + ': %s' % adm.maxlogins)
    msg(color('verbose', 'b') + ': %s' % 'yes' if adm.verbose else 'no')
    msg(color('capability', 'b') + ': %s' % ', '.join(adm.capab))
    msg(color('isonick', 'b') + ': %s' % ', '.join(adm.ison))
    msg(color('account', 'b') + ': %s' % ', '.join(adm.account))
    msg(color('hash_algorithm', 'b') + ': %s' % adm.hash_algorithm)
    msg(color('logins', 'b') + ': %s' % adm.logins)


@loader('admin add', 'admin edit !{account} !{option} !{value}+',
    need=[
        'requires nickserv',
        'registered user',
        'admin:superuser',
        'only:private'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.admin.admins',
        'syntax': 'admin edit syntax',
        'help': 'admin edit help'},
    record=':admins:')
def admin_edit(irc, ev, result, target, channel, _, locale):

    help = [
        'capability',
        'password',
        'maxlogins',
        'timeout',
        'verbose',
        'isonick',
        'account',
        'hash_algorithm']
