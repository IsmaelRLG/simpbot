# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import thread
import logging
import traceback
from re import compile as regex
from re import match
from re import escape
from .irc import irc
from . import config
from . import parser

logging = logging.getLogger('COMMANDS')
config.PREFIX = escape(config.PREFIX)


def CaptureError(func, irc, ev, SRE_Match, target, channel, _):
    try:
        func(irc, ev, SRE_Match, target, channel, _)
    except:
        logging.error(_('Excepcion producida por {mask}: {command}: {message}'))
        irc.verbose(_('Excepcion producida por {mask}: {command}: {message}'))
        line_n = 1
        for line in traceback.format_exc().splitlines():
            logging.error('Command Exception: ' + line)
            if not line_n in (2, 3):
                irc.verbose('[ERROR]: ' + line)
            line_n += 1


def msg(irc, ev):
    message = ev('message')
    target = ev('target')
    superregex = '^({}([:;, ] ?)|[{}])(?P<text>.*)'
    superregex = superregex.format(escape(irc.nickname), config.PREFIX)
    superregex = superregex if target != irc.nickname else '(?P<text>.*)'
    sre = match(superregex, message, 2)
    if sre is None:
        return
    else:
        message = sre.group('text')
    channel = None
    if target[0] == '#':
        channel = target

    if channel is None and target.lower() == irc.nickname.lower():
        target = ev('nick')

    for handler in msg.handlers:
        SRE_Match = handler['match'].match(message)

        if SRE_Match is None:
            continue

        _ = parser.replace(irc, SRE_Match)
        _['nickname'] = ev('nick')
        _['hostname'] = ev('host')
        _['nickname'] = ev('nick')
        _['helpmsg'] = parser.is_none(handler['help'])
        _['command'] = handler['alias']
        _['channel'] = parser.is_none(channel)
        _['message'] = ev('message')
        _['target'] = target
        _['mask'] = ev('mask')
        _['type'] = ev('type')
        CaptureError(handler['func'], irc, ev, SRE_Match, target, channel, _)
        return
irc.handlers.append({'func': msg,
    'match': regex(':((?P<mask>(?P<nick>.+)!(?P<user>.+)@(?P<host>[^ ]+))|'
    '(?P<machine>[^ ]+)) (?P<type>PRIVMSG|NOTICE) (?P<target>[^ ]+) '
    ':(?P<message>.*)', 2).match})


def addCommand(regex__, helpmsg=None, alias=None):
    def wrapper(func):
        if not hasattr(msg, 'handlers'):
            setattr(msg, 'handlers', [])
        if alias is None:
            name = func.func_name
        else:
            name = alias

        parse = parser.ParserRegex(regex__)
        msg.handlers.append({
            'match': regex(parse.string),
            'alias': name,
            'func': func,
            'help': helpmsg
        })

        def CommandHandler(irc, ev, SRE_Match, target, channel, _):
            args = (irc, ev, SRE_Match, target, channel, _)
            thread.start_new(func, args, {})

            def does_nothing(*args, **kwargs):
                pass
            return does_nothing(*(), **{})

        return CommandHandler
    return wrapper


def admin(func):
    def watchdog(irc, ev, SRE_Match, target, channel, _):
        if not ev('host') in config.ADMINS:
            irc.error(target, 'Permiso denegado.')
            irc.verbose(_('{mask}: Intentó usar: {command}'))

            def does_nothing(*args, **kwargs):
                pass
            return does_nothing(None)
        else:
            return func(irc, ev, SRE_Match, target, channel, _)
    return watchdog