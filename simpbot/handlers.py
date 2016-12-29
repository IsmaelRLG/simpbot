# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import time
import logging
from re import compile as regex
from . import __version__
from . import parser
from .irc import client
from .bottools import text
logging = logging.getLogger('HANDLERS')
client.handlers = []


# Agregar handlers ;D
########################################
def add_handler(func, regex_, noparse=True):
    if not noparse:
        regex_ = parser.ParserRegex(regex_).string
    client.handlers.append({'func': func, 'match': regex(regex_, 2).match})


# Decorador
########################################
def handler(Regex):
    Regex = parser.ParserRegex(Regex).string

    def addhandler(func):
        add_handler(func, Regex)
        return func
    return addhandler


# Parseadores
########################################
def rpl(code, *args):
    rpl_ = ':?(?P<machine>[^ ]+) {} (?P<me>[^ ]+) '.format(str(code).zfill(3))
    if len(args) > 0:
        rpl_ += ' '.join(args)
    return rpl_


def usr(value, *args):
    rpl_ = ':((?P<mask>(?P<nick>.+)!(?P<user>.+)@(?P<host>[^ ]+))|'
    rpl_ += '(?P<machine>[^ ]+)) %s ' % value
    if len(args) > 0:
        rpl_ += ' '.join(args)
    return rpl_


# Handlers
########################################

# Ping -> Pong
@handler('PING !{server}!{server2}?')
def pong(irc, ev):
    irc.pong(ev('server'), ev('server2') if ev('server2') else '')


# Capacidades del servidor
@handler(rpl(5, '!{feature}+( :are supported by this server)'))
def featurelist(irc, ev):
    for split in ev('feature').split():
        irc.features.load_feature(split)


# Registro completado
@handler(rpl(4, '!{servername} !{version} !{aum} !{acm}'))
def registration_successful(irc, ev):
    logging.info('Registro completado')
    irc.set_status('r')

    if irc.usens and irc.sasl is False:
        irc.privmsg('NickServ', 'ID %s %s' % irc.__nickserv)

    if irc.dbstore:
        for channel in irc.dbstore.store_chan.keys():
            key = irc.dbstore.store_chan[channel].key
            if not key:
                key = ''
            irc.join(channel, key)

    msg = '[%Z][%d/%m/%Y](%X): Conexión exitosa.'
    irc.verbose('connected', time.strftime(msg))


# Nick en uso
@handler(rpl(433, '!{nick} :!{msg}+'))
def err_nicknameinuse(irc, ev):
    irc.nickname = text.randphras(l=7, alpha=(False, True), noinitnum=True)
    irc.nick(irc.nickname)


# Error de conexión
@handler('ERROR !{message}')
def err_connection(irc, ev):
    time.sleep(4)
    if irc.connection_status in 'cr':
        if irc.request:
            irc.request.reset()

        irc.try_connect()


# Mantiene el nick real
@handler(usr('NICK', ':?!{new_nick}'))
def real_nick(irc, ev):
    if ev('nick').lower() == irc.nickname.lower():
        irc.nickname = ev('new_nick')
    else:
        if irc.request:
            irc.request.update_nick(ev('nick'), ev('new_nick'))
        return True


# Necesita de privilegios
@handler(rpl(482, '!{channel} :!{message}+'))
def err_chanoprivsneeded(irc, ev):
    irc.error(*ev('channel', 'message'))


# CTCP VERSION
@handler(usr('PRIVMSG', '!{target} :\001VERSION\001'))
def ctcp_version(irc, ev):
    irc.ctcp_reply(ev('nick'), 'SimpBot v%s' % __version__)


# CTCP PING
@handler(usr('PRIVMSG', '!{target} :\001PING !{code}\001'))
def ctcp_ping(irc, ev):
    irc.ctcp_reply(ev('nick'), 'PING ' + ev('code'))


# Mantiene los canales en que está el bot
@handler(usr('JOIN', ':?!{channel}'))
def join(irc, ev):
    if not irc.request:
        return True
    nick = ev('nick')
    channel = ev('channel')

    if nick.lower() == irc.nickname.lower():
        irc.request.set_chan(channel)
        irc.request.who(channel)
    else:
        user = irc.request.get_user(nick)
        if user is None:
            user = irc.request.set_user(ev('user'), ev('host'), nick)
            irc.request.request(nick, channel)
        chan = irc.request.get_chan(channel)
        chan.append(user)
        return True


# Mantiene los canales en que está el bot
@handler(usr('PART', '!{channel}!{message}+?'))
def part(irc, ev):
    if not irc.request:
        return True
    nick = ev('nick')
    channel = ev('channel')

    if nick.lower() == irc.nickname.lower():
        irc.request.del_chan(channel)
    else:
        user = irc.request.get_user(nick)
        if user is None:
            return  # ¿wtf?

        chan = irc.request.get_chan(channel)
        chan.remove(user)
        return True


# Mantiene los canales en que está el bot
@handler(usr('QUIT', ':!{message}+'))
def quit(irc, ev):
    if not irc.request:
        return True
    nick = ev('nick')

    if nick.lower() == irc.nickname.lower():
        irc.request.reset()
    else:
        irc.request.del_user(nick)
        return True


# Mantiene los canales en que está el bot
@handler(usr('KICK', '!{channel} !{victim} :!{message}+'))
def kick(irc, ev):
    if not irc.request:
        return True
    nick = ev('victim')
    channel = ev('channel')

    if nick.lower() == irc.nickname.lower():
        irc.request.del_chan(channel)
    else:
        user = irc.request.get_user(nick)
        if user is None:
            return  # ¿wtf?

        chan = irc.request.get_chan(channel)
        chan.remove(user)
        return True
