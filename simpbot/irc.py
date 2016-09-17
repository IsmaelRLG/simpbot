# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import ssl
import time
import logging
import traceback
import socket
import thread

from . import config
from .util import randphras
from .util import textwrap
from .util import unicode_to_str
#from pyrat import plugin

logging = logging.getLogger('IRC')


class irc:

    def __init__(self):
        self.connected = False
        self.__login__ = False
        self.input_alive = False
        self.lock = False
        self.socket = None
        self.ltm = 0

        # IRC - Default
        self.servname = config.NETWORK
        self.addr = config.SERVER
        self.port = config.PORT
        self.ssl = config.SSL
        self.servpass = config.SERVPASS

        if config.NICK == "":
            config.NICK = randphras(l=7, alpha=(False, True), noinitnum=True)
        if config.USER == "":
            config.USER = randphras(l=7, alpha=(False, True), noinitnum=True)
        self.nickname = config.NICK
        self.username = config.USER
        thread.start_new(self.test_connection, (), {})

    def buildsock(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.ssl:
            self.socket = ssl.wrap_socket(self.socket)

    def connect(self):
        if self.connected or self.__login__:
            return

        self.buildsock()
        while not self.connected:
            try:
                self.socket.connect((self.addr, self.port))
                self.connected = True
            except Exception:
                logging.error('Conexion fallida. (%s:%s)', self.addr, self.port)
                logging.info('Reintentando conectar en %ss...' % config.WTIME)
                time.sleep(config.WTIME)

        else:
            logging.info('Conexion establecida: %s (%s) puerto %s.',
            self.addr, self.socket.getpeername()[0], self.port)

        if self.servpass != '':
            self.passwd(self.servpass)

        if config.USENS is False:
            return
        elif config.SASL is True:
            # Simple Authentication and Security Layer (SASL) - RFC 4422
            # Copyright (C) The Internet Society (2006).
            pw = '{0}\0{0}\0{1}'.format(config.USERNAME, config.PASSWORD)
            self.send_raw('AUTHENTICATE PLAIN')
            self.send_raw('AUTHENTICATE ' + pw.encode('base64'))

    def login(self):
        self.user(self.username, self.nickname)
        self.nick(self.nickname)

    def input(self):
        while self.connected:
            self.input_alive = True
            try:
                recv = self.socket.recv(1024)
            except socket.error:
                self.try_connect()
                continue

            self.ltm = time.time()

            for text in recv.splitlines():
                logging.info('input(%s): %s', self.servname, text)
                self.proccess_handlers(text)

        else:
            self.input_alive = False

    def try_connect(self):
        if not self.lock:
            self.lock = True
        else:
            while self.lock:
                time.sleep(1)
            else:
                return

        if self.ltm != 0:
            self.ltm = 0

        self.connected = False
        if self.socket:
            self.socket.close()

        self.connect()
        if not self.input_alive:
            thread.start_new(self.input, (), {})
        self.login()
        self.lock = False

    def test_connection(self):
        while 1:
            time.sleep(1)
            if not self.connected or self.ltm == 0:
                continue

            if (time.time() - self.ltm) > config.TIMEOUT:
                logging.error('%s: Expiró el tiempo (%ss) de conexión.',
                self.servname, config.TIMEOUT)
                self.try_connect()

    def proccess_handlers(self, text):
        for handler in self.handlers:
            SRE_Match = handler['match'](text)
            if SRE_Match is not None:
                try:
                    exec_res = handler['func'](self, SRE_Match.group)
                except:
                    for line in traceback.format_exc().splitlines():
                        logging.error('Handler Exception: ' + line)
                else:
                    if exec_res is None:
                        return
                    else:
                        continue

    def send_raw(self, text):
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        try:
            self.socket.send(text + '\r\n')
            logging.info('output(%s): %s', self.servname, text)
            time.sleep(config.MSGPS)
        except socket.error:
            self.try_connect()

    ##########################################################################
    #                             Comandos IRC                               #
    ##########################################################################

    @unicode_to_str
    def ctcp(self, ctcptype, target, parameter=""):
        tmpl = (
            "\001{ctcptype} {parameter}\001" if parameter else
            "\001{ctcptype}\001"
        )
        self.privmsg(target, tmpl.format(**vars()))

    @unicode_to_str
    def ctcp_reply(self, target, parameter):
        self.notice(target, "\001%s\001" % parameter)

    @unicode_to_str
    def join(self, channel, key=""):
        self.send_raw("JOIN %s%s" % (channel, (key and (" " + key))))

    @unicode_to_str
    def kick(self, channel, nick, comment=""):
        tmpl = "KICK {channel} {nick}"
        if comment:
            tmpl += " :{comment}"
        self.send_raw(tmpl.format(**vars()))

    @unicode_to_str
    def nick(self, newnick):
        self.send_raw("NICK " + newnick)

    @unicode_to_str
    def notice(self, target, text):
        for line in textwrap(text):
            self.send_raw("NOTICE %s :%s" % (target, line))

    @unicode_to_str
    def part(self, channels, message=""):
        self.send_raw("PART %s%s" % (channels, (message and (" " + message))))

    @unicode_to_str
    def privmsg(self, target, text):
        for line in textwrap(text):
            self.send_raw("PRIVMSG %s :%s" % (target, line))

    def msg(self, target, text):
        self.notice(target, text)

    def verbose(self, text):
        if not config.VERBOSE:
            return

        for nick in config.VERBOSENICKS:
            self.notice(nick, text)

    @unicode_to_str
    def error(self, target, text):
        for line in textwrap(text):
            self.send_raw("NOTICE %s :[ERROR] %s" % (target, line))

    @unicode_to_str
    def passwd(self, password):
        self.send_raw("PASS " + password)

    @unicode_to_str
    def pong(self, target, target2=""):
        self.send_raw("PONG %s%s" % (target, target2 and (" " + target2)))

    @unicode_to_str
    def remove(self, channel, nick, comment=""):
        tmpl = "REMOVE {channel} {nick}"
        if comment:
            tmpl += " :{comment}"
        self.send_raw(tmpl.format(**vars()))

    @unicode_to_str
    def topic(self, channel, new_topic=None):
        if new_topic is None:
            self.send_raw("TOPIC " + channel)
        else:
            self.send_raw("TOPIC %s :%s" % (channel, new_topic))

    @unicode_to_str
    def user(self, username, realname):
        self.send_raw("USER %s 0 * :%s" % (username, realname))

    @unicode_to_str
    def quit(self, message=""):
        self.send_raw("QUIT" + (message and (" :" + message)))
