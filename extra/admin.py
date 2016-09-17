# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot


@simpbot.commands.addCommand('admin !{host}',
    'Agrega o elimina un administrador (temporalmente)', 'admin')
@simpbot.commands.admin
def admin(irc, ev, result, target, channel, _):
    if _['host'] == 'list':
        count = 1
        irc.msg(target, 'Admins totales: %s' % len(simpbot.config.ADMINS))
        irc.msg(target, ' NUMERO  | NOMBRE DE HOST')
        for hostname in simpbot.config.ADMINS:
            irc.msg(target, '[ %s ] | %s' % (str(count).zfill(4), hostname))
            count += 1
    elif _['host'] in simpbot.config.ADMINS:
        simpbot.config.ADMINS.remove(_['host'])
        irc.msg(target, _('host "{host}" removido de los administradores.'))
    else:
        simpbot.config.ADMINS.append(_['host'])
        irc.msg(target, _('Se agrego el host "{host}" a los administradores.'))
