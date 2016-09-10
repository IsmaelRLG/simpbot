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

logging = logging.getLogger('COMMANDS')
config.PREFIX = escape(config.PREFIX)


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
        SRE_Match = handler['match'](message)
        if SRE_Match is not None:
            try:
                handler['func'](irc, ev, SRE_Match, target, channel)
            except:
                for line in traceback.format_exc().splitlines():
                    logging.error('Command Exception: ' + line)
            finally:
                return
irc.handlers.append({'func': msg,
    'match': regex(':((?P<nick>.+)!(?P<user>.+)@(?P<host>[^ ]+)|'
    '(?P<machine>[^ ]+)) (PRIVMSG|NOTICE) (?P<target>[^ ]+) '
    ':(?P<message>.*)', 2).match})


def addCommand(regex__):
    def wrapper(func):
        if not hasattr(msg, 'handlers'):
            setattr(msg, 'handlers', [])

        msg.handlers.append({
            'match': regex(regex__).match,
            'func': func
        })

        def CommandHandler(*args, **kwargs):
            thread.start_new(func, args, kwargs)

            def does_nothing(*args, **kwargs):
                pass
            return does_nothing(*args, **kwargs)

        return CommandHandler
    return wrapper


def admin(func):
    def watchdog(irc, ev, SRE_Match, target, channel):
        if not ev('host') in config.ADMINS:
            irc.error(target, 'Permiso denegado.')

            def does_nothing(*args, **kwargs):
                pass
            return does_nothing(None)
        else:
            return func(irc, ev, SRE_Match, target, channel)
    return watchdog