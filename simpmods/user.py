# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot
from simpbot.bottools.irc import color
module = simpbot.get_module(sys=True)
loader = module.loader()


@loader('register user', 'register user', syntax="register user", need=[
    'requires nickserv',
    'unregistered user'])
def register(irc, ev, result, target, channel, _):
    """Registra algún usuario en el bot."""
    user = _['user']

    def check_max():
        ok = True
        no = False
        if irc.dbstore.max_users == 0:
            return ok
        total = len(irc.dbstore.store_request['chan'])
        total += irc.dbstore.total_user()
        error = 'Se alcanzó el límite de cuentas para solicitud ó registro.'
        if total < irc.dbstore.max_users:
            return ok
        elif (total + 1) == irc.dbstore.max_users:
            irc.verbose('request', 'NOTIFICACIÓN: ' + error)
        irc.error(target, error)
        return no

    if irc.dbstore.userregister == 'allow':
        if not check_max():
            return
        irc.dbstore.register_user(user.account)
        msg = _('Se registró la cuenta "{user.account}".')
        irc.notice(target, msg)
        irc.verbose('new user', msg)
    elif irc.dbstore.userregister == 'request':
        if irc.dbstore.has_request('user', user.account):
            irc.error(target, 'Ya tiene una solicitud abierta.')
            return
        if not check_max():
            return
        irc.dbstore.request('user', user.account)
        msg = '{user.nick} ({user.user@user.host}) solicita aprobación de la'
        msg += ' cuenta {user.account}, código de aprobación: "%s".'
        msg = msg % color(irc.dbstore.get_request(user.account)[0], 'b')
        irc.verbose('request', _(msg))
        irc.notice(target, _('Solicitud de cuenta "{user.account}" enviada.'))
    elif irc.dbstore.userregister == 'deny':
        irc.error(target, 'Se encuentra inhabilitado el registro de usuarios.')


@loader('drop user', 'drop user', syntax="drop user", need=[
    'requires nickserv',
    'registered user'])
def drop(irc, ev, result, target, channel, _):
    """Elimina algún usuario del bot."""
    user = _['user']
    msg = 'Para evitar el uso accidental de este comando, esta operación tiene '
    msg += 'que ser confirmada. Por favor confirme respondiendo con /'
    msg += color('msg {irc.nickname} confirm drop:user {hash}', 'b')
    if irc.dbstore.has_drop('user', user.account):
        _['hash'] = irc.dbstore.get_hashdrop(user.account)
    else:
        _['hash'] = irc.dbstore.drop('user', user.account)
    irc.notice(user.nick, _(msg))


@loader('confirm drop:user', 'confirm drop:user !{code}',
    syntax="confirm drop:user <código>", need=[
    'requires nickserv',
    'registered user'])
def confirm(irc, ev, result, target, channel, _):
    """Confirma la eliminación de un usuario del bot."""
    user = _['user']
    code = _['code']
    if len(code) != 32 or not irc.dbstore.has_drop('user', user.account) or \
    irc.dbstore.get_hashdrop(user.account) != code:
        irc.error(user.nick, 'Código de confirmación inválido.')
        return
    irc.dbstore.del_drop('user', user.account)
    irc.dbstore.drop_user(user.account)
    msg = _('Se eliminó la cuenta "{user.account}".')
    irc.notice(user.nick, msg)
    irc.verbose('drop user', msg)
