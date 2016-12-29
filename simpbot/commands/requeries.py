# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)


from simpbot.bottools import irc as irctools

requerimentls = {}
failed = True


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
        irc.error(target, 'No se encuentra logueado ó registrado en NickServ')
        return failed
requerimentls['requires nickserv'] = req_nickserv


def only(vars):
    irc = vars['self'].irc
    msg = vars['msg']
    args = vars['watchdog'][1]
    target = vars['user'].nick
    if len(args) == 0:
        irc.verbose('error', msg % 'Only; No se indicaron los parametros.')
        return failed

    msg = 'Este comando solo debe ser ejecutado en %s.'
    if args[0] == 'private':
        if vars['privbot']:
            return
        elif len(args) == 1:
            irc.error(target, msg % 'privado')
            return failed
    elif args[0] == 'channel':
        if not vars['privbot']:
            return
        elif len(args) == 1:
            irc.error(target, msg % 'un canal')
            return failed
requerimentls['only'] = only


def chan_register(vars):
    irc = vars['self'].irc
    msg = vars['msg']
    dbstore = irc.dbstore
    channel1 = vars['channel']
    channel2 = vars['watchdog'][1]
    privbot = vars['privbot']
    target = vars['target']
    if privbot:
        if len(channel2) == 0:
            irc.verbose('error', msg % 'Grupos no indicados.')
            return failed
        for group in channel2:
            try:
                channel = vars['result'].group(group)
            except (IndexError, KeyError):
                irc.verbose('error', msg % 'Grupo "%s" erróneo.' % group)
                return failed
            else:
                if channel is None:
                    continue
                if not irctools.ischannel(channel, irc=irc):
                    irc.error(target, 'Canal "%s" inválido.' % channel)
                    return failed
            if dbstore.get_chan(channel) is None:
                irc.error(target, 'Canal "%s" no registrado.' % channel)
                return failed
            vars['channel'] = channel
            return
        irc.error(target, 'Debe indicar un canal.')
        return failed
    elif len(channel2) > 0:

        try:
            channel = vars['result'].group(channel2[0])
        except (IndexError, KeyError):
            irc.verbose('error', msg % 'Grupo "%s" erróneo.' % channel2[0])
            return failed

        vars['channel'] = channel
        if dbstore.get_chan(channel) is None:
            irc.error(vars['target'], 'Canal "%s" no registrado.' % channel)
            return failed
    elif dbstore.get_chan(channel1) is None:
        irc.error(vars['target'], 'Canal "%s" no registrado.' % channel1)
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
    if privbot:
        if len(channel2) == 0:
            irc.verbose('error', msg % 'Grupos no indicados.')
            return failed
        for group in channel2:
            try:
                channel = vars['result'].group(group)
            except (IndexError, KeyError):
                irc.verbose('error', msg % 'Grupo "%s" erróneo.' % group)
                return failed
            else:
                if channel is None:
                    continue
                if not irctools.ischannel(channel, irc=irc):
                    irc.error(target, 'Canal "%s" inválido.' % channel)
                    return failed
            if dbstore.get_chan(channel) is not None:
                irc.error(target, 'Canal "%s" registrado.' % channel)
                return failed
            vars['channel'] = channel
            return
        irc.error(target, 'Debe indicar un canal.')
        return failed
    elif len(channel2) > 0:

        try:
            channel = vars['result'].group(channel2[0])
        except (IndexError, KeyError):
            irc.verbose('error', msg % 'Grupo "%s" erróneo.' % channel2[0])
            return failed

        vars['channel'] = channel
        if dbstore.get_chan(channel) is not None:
            irc.error(vars['target'], 'Canal "%s" registrado.' % channel)
            return failed
    elif dbstore.get_chan(channel1) is not None:
        irc.error(vars['target'], 'Canal "%s" registrado.' % channel1)
        return failed
requerimentls['unregistered chan'] = unregistered_chan


def user_register(vars):
    irc = vars['self'].irc
    msg = vars['msg']
    user = vars['user']
    args = vars['watchdog'][1]
    target = user.nick
    dbstore = irc.dbstore
    if len(args) == 0:
        if dbstore.get_user(user.account) is None:
            irc.error(target, 'No se encuentra registrado en el bot.')
            return failed
        return

    try:
        usr = vars['result'].group(args[0])
    except (IndexError, KeyError):
        irc.verbose('error', msg % 'Grupo "%s" erróneo.' % args[0])
        return failed

    if usr is None:
        if 'optional' in args:
            return
        else:
            return failed

    if '*' in usr or '@' in usr:
        irc.error(target, 'Usuario "%s" inválido.' % usr)
        return failed

    if dbstore.get_user(usr) is None:
        irc.error(target, 'Usuario "%s" no registrado en el bot.' % usr)
requerimentls['registered user'] = user_register


def unregistered_user(vars):
    irc = vars['self'].irc
    user = vars['user']
    target = user.nick
    dbstore = irc.dbstore
    if dbstore.get_user(user.account) is not None:
        irc.error(target, 'Se encuentra registrado en el bot.')
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
        irc.verbose('error', msg % 'No se indicaron los flags.')
        return failed
    if not args[0].isalnum():
        irc.verbose('error', msg % 'Flags "%s" inválido.' % args[0])
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
        irc.error(target, '[Permiso denegado]: No tiene los permisos necesarios'
        ' para ejecutar esta acción, necesita: +%s.' % args[0])
        return failed
requerimentls['flags'] = flags


def admin(vars):
    irc = vars['self'].irc
    msg = vars['msg']
    user = vars['user']
    args = vars['watchdog'][1]
    tar = user.nick
    dbstore = irc.dbstore

    usr = dbstore.get_user(user.account)
    if not usr.isadmin():
        irc.error(tar, '[Permiso denegado]: Comando sólo para administradores.')
        return failed

    if len(args) == 0:
        return
    print args

    for capab in args:
        if not usr.admin.has_capab(capab):
            irc.error(tar, '[Permiso denegado]: No posee los permisos '
            'suficientes para ejecutar esta acción.')
            irc.verbose('fail use', msg % ('Intento de uso por: {}, Cuenta del '
            'administrador: {}').format(user.mask, usr.admin.user))
            return failed
requerimentls['admin'] = admin