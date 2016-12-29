# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot
from simpbot.bottools.irc import color
module = simpbot.get_module(sys=True)
loader = module.loader()


@loader('help', 'help!{command_name}+?', syntax='help <comando (opcional)>')
def help(irc, ev, result, target, channel, _):
    user = _['user']
    if irc.dbstore.has_user(user.account):
        user_is_admin = irc.dbstore.get_user(user.account).isadmin()
    else:
        user_is_admin = False

    motd = 'SimpBot v{version} - Codigo fuente: {url}'
    motd = motd.format(version=simpbot.__version__, url='https://goo.gl')
    command = _['command_name'].lower().strip()
    usrcmd = []
    admcmd = []
    if command == '':
        for simpmod in simpbot.modules.core.values():
            for name, handler in simpmod.handlers.items():
                next = False  # lint:ok
                for need in handler.need:
                    if need.startswith('admin:'):
                        admcmd.append(name)
                        next = True  # lint:ok
                        break
                else:
                    if next:
                        continue
                    else:
                        usrcmd.append(name)

        usrcmd.sort()
        admcmd.sort()
        _['prefix'] = ', '.join([color(l, 'b') for l in irc.prefix])
        irc.notice(target, motd)
        irc.notice(target, _('Prefijo: {prefix}. Comandos disponibles:'))
        irc.notice(target, ', '.join(usrcmd))
        if user_is_admin:
            irc.notice(target, ' ')
            irc.notice(target, '---- Comandos para administradores ----')
            irc.notice(target, ', '.join(admcmd))
        irc.notice(target, ' ')
        moreinfo = 'Para obtener mas información sobre un comando en especifico'
        moreinfo += ', por favor enviar: '
        if _['privbot']:
            moreinfo += color(_('help <comando>'), 'b')
        else:
            moreinfo += color(_('{irc.nickname}: help <comando>'), 'b')
        return irc.notice(target, moreinfo)

    similar = []
    handler = []

    for simpmod in simpbot.modules.core.values():
        for name, CommandHandler in simpmod.handlers.items():
            need_admin = False
            name = name.lower()
            for need in CommandHandler.need:
                if need.startswith('admin:'):
                    need_admin = True
                    break
            if name == command:
                if need_admin and not user_is_admin:
                    continue
                else:
                    handler.append(CommandHandler)
            elif name.find(command) != -1:
                if need_admin and not user_is_admin:
                    continue
                else:
                    similar.append(name)

    if len(handler) > 0:
        handler = handler[0]
        if not handler.helpmsg:
            msg = 'El comando ' + color(_(command), 'b') + 'no cuenta con una '
            msg += 'ayuda'
            if handler.syntax:
                msg += 'definida, pero si cuenta con la siguiente sintaxis:'
                irc.error(target, msg)
                irc.notice(target, color(_('Sintaxis: '), 'b') + handler.syntax)
            else:
                irc.error(target, msg + ' ni una sintaxis definida.')
            return

        irc.notice(target, motd)
        irc.notice(target, 'Ayuda del comando ' + color(_(command), 'b') + ':')
        for line in handler.helpmsg.splitlines():
            try:
                irc.notice(target, _(line))
            except:
                irc.notice(target, line)
        if handler.syntax:
            irc.notice(target, color(_('Sintaxis: '), 'b') + handler.syntax)
        irc.notice(target, 'Fin de la ayuda de ' + color(_(command), 'b'))

    else:
        irc.error(target, 'No existe el comando ' + color(_(command), 'b'))
        if len(similar) > 0:
            irc.notice(target, 'Quizás quiso decir: ' + ', '.join(similar))