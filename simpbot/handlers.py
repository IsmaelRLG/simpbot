# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import time
import logging
from re import compile as regex
from . import config
from . import __version__
from .irc import irc
from .util import randphras
logging = logging.getLogger('HANDLERS')
irc.handlers = []


# Ping -> Pong
def pong(irc, ev):
    irc.pong(ev('server'), ev('server2') if ev('server2') else '')
irc.handlers.append({'func': pong,
    'match': regex('PING (?P<server>[^ ]+)( (?P<server2>[^ ]+))?', 2).match})


# Registro completado
def registration_successful(irc, ev):
    logging.info('Registro completado')

    if config.USENS is True and config.SASL is False:
        irc.privmsg('NickServ', 'ID %s %s' % (config.USERNAME, config.PASSWORD))

    for channel in config.CHANNELS:
        channel = channel.split(' ', 1)
        irc.join(*channel)

    irc.verbose(time.strftime('[%Z][%d/%m/%Y](%X): Conexión exitosa.'))
irc.handlers.append({'func': registration_successful, 'match': regex(
    ':?(?P<machine>[^ ]+) 004 (?P<me>[^ ]+) (?P<servername>[^ ]+) '
    '(?P<version>[^ ]+) (?P<aum>[^ ]+) (?P<acm>[^ ]+)', 2).match})


# Nick en uso
def err_nicknameinuse(irc, ev):
    irc.nickname = randphras(l=7, alpha=(False, True), noinitnum=True)
    irc.nick(irc.nickname)
irc.handlers.append({'func': err_nicknameinuse, 'match': regex(
    ':?(?P<machine>[^ ]+) 433 (?P<me>[^ ]+) '
    '(?P<nick>[^ ]+) :(?P<message>.*)', 2).match})


# Error de conexion
def err_connection(irc, ev):
    time.sleep(4)
    irc.try_connect()
irc.handlers.append({'func': err_connection,
    'match': regex('ERROR (?P<message>.*)', 2).match})


# Mantiene el nick real
def real_nick(irc, ev):
    if ev('nick').lower() == irc.nickname.lower():
        irc.nickname = ev('new_nick')
    else:
        return True
irc.handlers.append({'func': real_nick,
    'match': regex(':((?P<nick>.+)!(?P<user>.+)@(?P<host>[^ ]+)|'
    '(?P<machine>[^ ]+)) NICK :(?P<new_nick>.*)', 2).match})


# Necesita de privilegios
def err_chanoprivsneeded(irc, ev):
    irc.error(*ev('channel', 'message'))
irc.handlers.append({'func': err_chanoprivsneeded, 'match': regex(
    ':?(?P<machine>[^ ]+) 482 (?P<me>[^ ]+) '
    '(?P<channel>[^ ]+) :(?P<message>.*)', 2).match})


# CTCP VERSION
def ctcp_version(irc, ev):
    irc.ctcp_reply(ev('nick'), 'SimpleBot v%s' % __version__)
irc.handlers.append({'func': ctcp_version,
    'match': regex(':((?P<nick>.+)!(?P<user>.+)@(?P<host>[^ ]+)|'
    '(?P<machine>[^ ]+)) PRIVMSG (?P<target>[^ ]+) '
    ':\001VERSION\001$', 2).match})


# CTCP PING
def ctcp_ping(irc, ev):
    irc.ctcp_reply(ev('nick'), 'PING ' + ev('code'))
irc.handlers.append({'func': ctcp_ping,
    'match': regex(':((?P<nick>.+)!(?P<user>.+)@(?P<host>[^ ]+)|'
    '(?P<machine>[^ ]+)) PRIVMSG (?P<target>[^ ]+) '
    ':\001PING (?P<code>[^ ]+)\001$', 2).match})