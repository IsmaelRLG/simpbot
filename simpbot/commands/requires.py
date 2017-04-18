# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)


from simpbot.bottools import irc as irctools
from simpbot import localedata


requerimentls = {}
logging = __import__('logging').getLogger('requires')
failed = True
i18n = localedata.get()


def get(requeriment):
    """
    get('admin:simple')
    """
    args = []
    if isinstance(requeriment, tuple) or isinstance(requeriment, list):
        return requeriment
    elif ':' in requeriment:
        requeriment = requeriment.split(':', 1)
        if requeriment[1] != '':
            if ',' in requeriment[1]:
                args.extend(requeriment[1].split(','))
            else:
                args.append(requeriment[1])
        requeriment = requeriment[0]

    if requeriment in requerimentls:
        return requerimentls[requeriment], args


def req_nickserv(vars):
    irc = vars['self'].irc
    user = vars['user']
    target = vars['target']
    if user.account is None:
        irc.error(target, localedata.get(vars['lang'])['not logged'])
        return failed
requerimentls['requires nickserv'] = req_nickserv


def only(vars):
    irc = vars['self'].irc
    args = vars['watchdog'][1]
    target = vars['user'].nick
    if len(args) == 0:
        logging.error(vars['msg'] % i18n['without params'] % 'only')
        return failed

    if args[0] == 'private':
        if vars['privbot']:
            return
        elif len(args) == 1:
            irc.error(target, localedata.get(vars['lang'])['only private'])
            return failed
    elif args[0] == 'channel':
        if not vars['privbot']:
            return
        elif len(args) == 1:
            irc.error(target, localedata.get(vars['lang'])['only channel'])
            return failed
requerimentls['only'] = only


def chan_register(vars):
    irc = vars['self'].irc
    msg = vars['msg']
    dbstore = irc.dbstore
    channel = vars['channel']
    privbot = vars['privbot']
    target = vars['target']
    locale = localedata.get(vars['lang'])
    result = vars['result']
    tgroup = {}
    groupnames = vars['watchdog'][1]
    non_channel = (len(groupnames) > 0 and groupnames[0] == 'non-channel')
    for group in groupnames:
        if not '=' in group:
            continue

        try:
            v, group = group.split('=', 1)
        except ValueError:
            continue
        tgroup[v] = group.split()

    if privbot and not non_channel:

        if len(groupnames) == 0:
            logging.error(msg % i18n['without params'] % 'chan_register')
            return failed

        for group in (tgroup['private'] if 'private' in tgroup else groupnames):
            try:
                channel = result.group(group)
            except (IndexError, KeyError):
                logging.error(msg % i18n['invalid params'] % 'chan_register')
                return failed
            else:
                if channel is None:
                    continue
                if not irctools.ischannel(channel, irc=irc):
                    irc.error(target, locale['invalid channel'] % channel)
                    return failed
            if dbstore.get_chan(channel) is None:
                irc.error(target, locale['unregistered channel'] % channel)
                return failed
            vars['channel'] = channel
            return
        irc.error(target, locale['channel needed'])
        return failed
    elif len(groupnames) > 0:
        try:
            if 'channel' in tgroup:
                if tgroup['channel'][0] == 'non-channel':
                    assert False
                else:
                    groupname = tgroup['channel'][0]
            else:
                groupname = groupnames[0]

            if not non_channel:
                channel = vars['result'].group(groupname)
        except AssertionError:
            pass
        except (IndexError, KeyError):
            irc.verbose('error', msg % i18n['invalid params'] % 'chan_register')
            return failed

        vars['channel'] = channel
        if dbstore.get_chan(channel) is None:
            if not non_channel:
                irc.error(target, locale['unregistered channel'] % channel)
            return failed
    elif dbstore.get_chan(channel) is None:
        if not non_channel:
            irc.error(target, locale['unregistered channel'] % channel)
        return failed

requerimentls['registered chan'] = chan_register


def unregistered_chan(vars):
    irc = vars['self'].irc
    msg = vars['msg']
    dbstore = irc.dbstore
    channel1 = vars['channel']
    channel2 = vars['watchdog'][1]
    privbot = vars['privbot']
    target = vars['target']
    locale = localedata.get(vars['lang'])
    if privbot:
        if len(channel2) == 0:
            logging.error(msg % i18n['without params'] % 'unregistered_chan')
            return failed
        for group in channel2:
            try:
                channel = vars['result'].group(group)
            except (IndexError, KeyError):
                logging.error(msg % i18n['invalid params'] % 'unregistered_chan')
                return failed
            else:
                if channel is None:
                    continue
                if not irctools.ischannel(channel, irc=irc):
                    irc.error(target, locale['invalid channel'] % channel)
                    return failed
            if dbstore.get_chan(channel) is not None:
                irc.error(target, locale['registered channel'] % channel)
                return failed
            vars['channel'] = channel
            return
        irc.error(target, )
        return failed
    elif len(channel2) > 0:

        try:
            channel = vars['result'].group(channel2[0])
        except (IndexError, KeyError):
            logging.error(msg % i18n['invalid params'] % 'unregistered_chan')
            return failed

        vars['channel'] = channel
        if dbstore.get_chan(channel) is not None:
            irc.error(vars['target'], locale['registered channel'] % channel)
            return failed
    elif dbstore.get_chan(channel1) is not None:
        irc.error(vars['target'], locale['registered channel'] % channel1)
        return failed
requerimentls['unregistered chan'] = unregistered_chan


def user_register(vars):
    irc = vars['self'].irc
    msg = vars['msg']
    user = vars['user']
    args = vars['watchdog'][1]
    target = user.nick
    locale = localedata.get(vars['lang'])
    dbstore = irc.dbstore
    if len(args) == 0:
        if user.account is None:
            irc.error(target, locale['not logged'])
            return failed

        if dbstore.get_user(user.account) is None:
            irc.error(target, locale['you are not registered'])
            return failed
        return

    try:
        usr = vars['result'].group(args[0])
    except (IndexError, KeyError):
        logging.error(msg % i18n['invalid params'] % 'user_register')
        return failed

    if usr is None:
        if 'optional' in args:
            return
        else:
            return failed

    if '*' in usr or '@' in usr or '!' in usr:
        irc.error(target, locale['invalid user'] % usr)
        return failed

    if dbstore.get_user(usr) is None:
        irc.error(target, locale['user no registered'] % usr)
requerimentls['registered user'] = user_register


def unregistered_user(vars):
    irc = vars['self'].irc
    user = vars['user']
    target = user.nick
    dbstore = irc.dbstore
    if dbstore.get_user(user.account) is not None:
        irc.error(target, localedata.get(vars['lang'])['already registered'])
        return failed
    return
requerimentls['unregistered user'] = unregistered_user


def flags(vars):
    irc = vars['self'].irc
    msg = vars['msg']
    user = vars['user']
    args = vars['watchdog'][1]
    channel = vars['channel']
    target = user.nick
    dbstore = irc.dbstore

    if len(args) == 0:
        logging.error(msg % i18n['without params'] % 'flags')
        return failed
    if not args[0].isalnum():
        logging.error(msg % i18n['invalid params'] % 'flags')
        return failed

    chan = dbstore.get_chan(channel)
    flag = chan.get_flags(dbstore.get_user(user.account))
    error = False
    if flag is None:
        flag = chan.get_flags(user.mask)
        if flag is None or not args[0] in flag:
            error = True
    elif not args[0] in flag:
        error = True

    if error:
        locale = localedata.get(vars['lang'])
        irc.error(target, locale['permission denied'] % args[0])
        return failed
requerimentls['flags'] = flags


def admin(vars):
    irc = vars['self'].irc
    msg = vars['msg']
    user = vars['user']
    args = vars['watchdog'][1]
    tar = user.nick
    dbstore = irc.dbstore
    locale = localedata.get(vars['lang'])

    usr = dbstore.get_user(user.account)
    if not usr.isadmin():
        # this line has been commented for security reasons, please
        # uncomment this line if you are sure of what makes
        #irc.error(tar, locale['only admins'])
        return failed

    if len(args) == 0:
        return

    for capab in args:
        if not usr.admin.has_capab(capab):
            irc.error(tar, locale['no capabs'])

            _ = vars['_']
            _['usr'] = usr
            irc.verbose('fail use', msg % _(locale['fail use']))
            return failed
requerimentls['admin'] = admin


def channel_status(vars):
    chan_name = vars['channel']
    irc       = vars['irc']
    target    = vars['target']
    mode_req  = vars['watchdog'][1]
    locale    = localedata.get(vars['lang'])

    channel = irc.request.get_chan(chan_name)
    if channel is None:
        irc.error(target, locale['not on the channel'] % chan_name)
        return failed

    status_bot = channel.get_user(irc.nickname).get_status(chan_name)
    print [status_bot]
    if status_bot == '':
        #irc.error(target, locale['mode required'] % '|+'.join(mode_req))
        return

    if not hasattr(irc.features, 'modeprefix'):
        irc.features.modeprefix = {}
        for char, mode in irc.features.prefix.items():
            irc.features.modeprefix[mode] = char

    prefix = irc.features.modeprefix
    for mode in mode_req:
        if not mode in prefix:
            continue
        char = prefix[mode]
        if char in status_bot:
            return

    irc.error(target, locale['mode required'] % '|+'.join(mode_req))
    return failed
requerimentls['channel_status'] = channel_status