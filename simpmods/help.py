# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import simpbot
from simpbot.bottools.irc import color
module = simpbot.get_module(sys=True)
loader = module.loader()
url_src = 'https://github.com/IsmaelRLG/simpbot'


@loader('help', 'help!{command_name}+?',
    #syntax='help <comando (opcional)>'
    #need=['only:private'],

    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'simpmods.help',
        'syntax': 'syntax',
        'help': 'help'})
def help(irc, ev, result, target, channel, _, locale):
    user = _['user']
    if irc.dbstore.has_user(user.account):
        user_is_admin = irc.dbstore.get_user(user.account).isadmin()
    else:
        user_is_admin = False

    motd = locale['motd']
    motd = motd.format(version=simpbot.__version__, url=url_src)
    command = _['command_name'].lower().strip()
    usrcmd = []
    admcmd = []
    if command == '':
        for simpmod in simpbot.modules.core.values():
            for name, handler in simpmod.handlers.items():
                if handler.regex is None and not handler.has_syntax() and \
                not handler.has_helpmsg() and not handler.has_alias():
                    continue

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
        irc.notice(target, _(locale['available commands']))
        irc.notice(target, ', '.join(usrcmd))
        if user_is_admin:
            irc.notice(target, ' ')
            irc.notice(target, '---- %s ----' % locale['admins commands'])
            irc.notice(target, ', '.join(admcmd))
        #irc.notice(target, ' ')
        if _['privbot']:
            msg = _(locale['more help (private)'])
        else:
            msg = _(locale['more help (channel)'])
        return irc.notice(target, msg)

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
        _['command'] = command
        if not handler.has_helpmsg():

            if handler.has_syntax():
                #irc.error(target, _(locale['not help and syntax']))
                for syn in handler.get_help(locale.lang, 'syntax').splitlines():
                    irc.notice(target, locale['syntax for'] % syn)
            else:
                irc.error(target, _(locale['not help and not syntax']))
            return

        irc.notice(target, motd)
        irc.notice(target, _(locale['help for']))
        try:
            irc.notice(target, _(handler.get_help(locale.lang, 'help')))
        except:
            irc.notice(target, handler.get_help(locale.lang, 'help'))

        if handler.has_syntax():
               for syn in handler.get_help(locale.lang, 'syntax').splitlines():
                    irc.notice(target, locale['syntax for'] % syn)

        req_flags = []
        for n in handler.neeed:
            if n.startswith('flags:'):
                req_flags.append(n.split(':')[1])
        if len(req_flags) > 0:
            irc.notice(target, locale['required flags'] % ''.join(req_flags))
        irc.notice(target, _(locale['end of']))

    else:
        irc.error(target, _(locale['command not found']))
        if len(similar) > 0:
            irc.notice(target, locale['suggest'] % ', '.join(similar))