# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot


@simpbot.commands.addCommand('help!{comando}+?', 'Muestra la ayuda', 'help')
def help(irc, ev, result, target, channel, _):
    print repr(simpbot.config.PREFIX.replace('\\', ''))
    _['prefix'] = str(simpbot.config.PREFIX.replace('\\', '')),
    _['version'] = simpbot.__version__
    irc.msg(target, _('SimpBot v{version}'))

    if _['comando'] is None:
        irc.msg(target, _('Prefijo: {prefix}. Comandos disponibles:'))
        cmd = [cmd['alias'] for cmd in simpbot.commands.msg.handlers]
        irc.msg(target, ', '.join(cmd))
        return

    helpmsg = None
    for cmd in simpbot.commands.msg.handlers:
        if cmd['alias'].lower() == _['comando'].lower():
            helpmsg = cmd['help']
            break
        else:
            continue

    if helpmsg is None:
        irc.error(target, _('No hay ayuda para "{comando}"'))
    else:
        irc.msg(target, _('Prefijo: {prefix}. Ayuda de {comando}'))
        irc.msg(target, helpmsg)
