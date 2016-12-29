# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import ssl
import time
import logging
import traceback
import socket
import thread
import Queue

from . import buffer
from . import features
from . import __version__
from .bottools import text

logging = logging.getLogger('IRC')

regexmsg = __import__('re').compile(
    ':(?P<mask>(?P<nick>.+)!(?P<user>.+)@(?P<host>[^ ]+)) '
    '(?P<type>PRIVMSG|NOTICE) (?P<target>[^ ]+) :(?P<message>.+)', 2)


class client:

    def __init__(self, netw, addr, port, nick, user, nickserv=None, sasl=None,
        timeout=240, msgps=.5, wtime=30, servpass=None, prefix='!'):
        self.connected = False
        self.connection_status = 'n'
        self.input_alive = False
        self.output_alive = False
        self.lock = False
        self.socket = None
        self.input_buffer = None
        self.output_buffer = Queue.Queue()
        self.features = features.FeatureSet()
        self.plaintext = False

        self.dbstore = None
        self.request = None
        self.commands = None

        # IRC - Default
        self.servname = netw
        self.addr = addr
        self.ssl = False
        if isinstance(port, basestring):
            if port.startswith('+'):
                self.ssl = True
                port = port.replace('+', '')
            if port.isdigit():
                port = int(port)
            else:
                port = 6667
        elif isinstance(port, float) or isinstance(port, int):
            port = int(port)
        self.port = port

        # IRC - Extra
        self.servpass = servpass
        self.__nickserv = nickserv
        self.usens = bool(self.__nickserv)
        self.sasl = sasl
        self.timeout = timeout
        self.msgps = msgps
        self.wtime = wtime
        self.prefix = prefix

        if nick == "" or nick[0].isdigit():
            nick = text.randphras(l=7, alpha=(False, True), noinitnum=True)
        if user == "" or user[0].isdigit():
            user = text.randphras(l=7, alpha=(False, True), noinitnum=True)
        self.nickname = nick
        self.username = user

    def __del__(self):
        self.disconnect()
        self.set_status('s')
        if self.dbstore:
            self.dbstore.save()

    def set_status(self, modes):
        """
        mode:
            n: Sin conectar
            c: Conectado
            r: Conectado y registrado
            p: Conexión perdida
            d: Desconectado
        """
        self.connection_status = modes[0]

    def connect(self, servpass=None):
        if self.connection_status in 'cr':
            return

        while self.connection_status in 'np':
            try:
                self.socket = socket.socket()
                self.socket.settimeout(self.timeout)
                self.input_buffer = buffer.LineBuffer()
                if self.ssl:
                    self.socket = ssl.wrap_socket(self.socket)
                self.socket.connect((self.addr, self.port))
                self.set_status('c')
            except Exception as error:
                logging.error('Conexión fallida. (%s:%s): %s',
                self.addr, self.port, str(error))
                logging.info('Reintentando conectar en %ss...' % self.wtime)
                time.sleep(self.wtime)

        else:
            logging.info('Conexión establecida: %s (%s) puerto %s.',
            self.addr, self.socket.getpeername()[0], self.port)

        if servpass is not None:
            self.servpass = servpass

        if self.servpass is not None:
            self.passwd(self.servpass)

        if self.__nickserv is None:
            return
        elif self.sasl:
            # Simple Authentication and Security Layer (SASL) - RFC 4422
            # Copyright (C) The Internet Society (2006).
            pw = '{0}\0{0}\0{1}'.format(self.sasl[0], self.sasl[1])
            self.send_raw('AUTHENTICATE PLAIN')
            self.send_raw('AUTHENTICATE ' + pw.encode('base64'))

    @property
    def connected(self):
        return self.connection_status == 'c' or self.connection_status == 'r'

    def reconnect(self, msg=""):
        self.disconnect(msg)
        if self.connection_status == 'd':
            self.set_status('n')
        self.try_connect()

    def disconnect(self, msg=""):
        if self.connection_status in 'cr':
            self.quit(msg)
            time.sleep(2.5)
            self.set_status('d')
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
            if self.request:
                self.request.reset()
            self.output_buffer.put(0)

    def login(self):
        self.user(self.username, self.nickname)
        self.nick(self.nickname)

    def output(self):
        while self.connection_status in 'crp':
            self.output_alive = True
            try:
                text = self.output_buffer.get(timeout=self.timeout)
            except Queue.Empty:
                if self.connection_status in 'cr':
                    self.set_status('p')
                    self.try_connect()

            if isinstance(text, unicode):
                text = text.encode('utf-8')
            elif text == 0:
                break
            elif not isinstance(text, basestring):
                logging.warning('se intentó enviar un tipo de dato inválido.')
                continue

            try:
                self.socket.send(text + '\r\n')
            except socket.error:
                if self.connection_status in 'cr':
                    self.set_status('p')
                    self.try_connect()

            if self.plaintext:
                logging.info('output(%s): %s', self.servname, text)
            time.sleep(self.msgps)
        else:
            self.input_alive = False

    def input(self):
        while self.connection_status in 'crp':
            self.input_alive = True
            try:
                recv = self.socket.recv(1024)
            except socket.timeout:
                logging.error('%s: Expiró el tiempo (%ss) de conexión.',
                self.servname, self.timeout)
                if self.connection_status in 'cr':
                    self.set_status('p')
                    self.try_connect()
                continue
            except socket.error:
                if self.connection_status in 'cr':
                    self.set_status('p')
                    self.try_connect()
                continue
            else:
                if recv == '':
                    if self.connection_status in 'cr':
                        self.set_status('p')
                        self.try_connect()
                    continue
                self.input_buffer.feed(recv)

            for line in self.input_buffer:
                if not line:
                    continue
                if self.plaintext:
                    logging.info('input(%s): %s', self.servname, line)
                msg = regexmsg.match(line)
                if msg and self.commands:
                    self.commands.put(msg)
                    continue

                self.proccess_handlers(line)
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

        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        #try:
        self.connect()
        #except KeyboardInterrupt:
         #   self.lock = False
         #   return

        if not self.input_alive:
            thread.start_new(self.input, (), {})
        if not self.output_alive:
            thread.start_new(self.output, (), {})
        else:
            while not self.output_buffer.empty():
                self.output_buffer.get()

        self.login()
        self.lock = False

    def proccess_handlers(self, text):
        for handler in self.handlers:
            SRE_Match = handler['match'](text)
            if SRE_Match is not None:
                logging.debug('Ejecutando: %s', handler['func'].func_name)
                try:
                    exec_res = handler['func'](self, SRE_Match.group)
                except:
                    for line in traceback.format_exc().splitlines():
                        print line
                        logging.error('Handler Exception: ' + line)
                else:
                    if exec_res is None:
                        return
                    else:
                        #logging.debug('Handler %s participa continuar',
                        #handler['func'].func_name)
                        continue

    def send_raw(self, text):
        if self.connection_status in 'npds':
            return
        self.output_buffer.put(text)

    ##########################################################################
    #                             Comandos IRC                               #
    ##########################################################################

    @text.unicode_to_str
    def ctcp(self, ctcptype, target, parameter=""):
        tmpl = (
            "\001{ctcptype} {parameter}\001" if parameter else
            "\001{ctcptype}\001"
        )
        self.privmsg(target, tmpl.format(**vars()))

    @text.unicode_to_str
    def ctcp_reply(self, target, parameter):
        self.notice(target, "\001%s\001" % parameter)

    @text.unicode_to_str
    def join(self, channel, key=""):
        self.send_raw("JOIN %s%s" % (channel, (key and (" " + key))))

    @text.unicode_to_str
    def kick(self, channel, nick, comment=""):
        tmpl = "KICK {channel} {nick}"
        if comment:
            tmpl += " :{comment}"
        self.send_raw(tmpl.format(**vars()))

    @text.unicode_to_str
    def invite(self, nick, channel):
        self.send_raw(" ".join(["INVITE", nick, channel]).strip())

    @text.unicode_to_str
    def nick(self, newnick):
        self.send_raw("NICK " + newnick)

    @text.unicode_to_str
    def notice(self, target, msg):
        for line in text.part(msg, 256):
            self.send_raw("NOTICE %s :%s" % (target, line))

    @text.unicode_to_str
    def part(self, channels, message=""):
        self.send_raw("PART %s%s" % (channels, (message and (" " + message))))

    @text.unicode_to_str
    def privmsg(self, target, msg):
        for line in text.part(msg, 256):
            self.send_raw("PRIVMSG %s :%s" % (target, line))

    def msg(self, target, text):
        self.notice(target, text)

    @text.unicode_to_str
    def mode(self, target, command):
        self.send_raw("MODE %s %s" % (target, command))

    def verbose(self, capab, text):
        if not self.dbstore or not self.connection_status in 'r':
            return

        capab = 'verbose:' + capab
        ison = []
        for user in self.dbstore.admins_list():
            if user.admin.has_capab(capab):
                ison.extend(user.admin.ison)
        print(capab, text)
        for target in ison:
            self.notice(target, text)

    @text.unicode_to_str
    def error(self, target, msg):
        for line in text.part(msg, 256, '... '):
            self.send_raw("NOTICE %s :[ERROR]: %s" % (target, line))

    @text.unicode_to_str
    def passwd(self, password):
        self.send_raw("PASS " + password)

    @text.unicode_to_str
    def pong(self, target, target2=""):
        self.send_raw("PONG %s%s" % (target, target2 and (" " + target2)))

    @text.unicode_to_str
    def remove(self, channel, nick, comment=""):
        tmpl = "REMOVE {channel} {nick}"
        if comment:
            tmpl += " :{comment}"
        self.send_raw(tmpl.format(**vars()))

    @text.unicode_to_str
    def who(self, target):
        if self.request:
            self.request.who(target)
        else:
            self._who(target)

    @text.unicode_to_str
    def _who(self, target="", op=""):
        self.send_raw("WHO%s%s" % (target and (" " + target), op and (" o")))

    @text.unicode_to_str
    def whois(self, target):
        if self.request:
            self.request.whois(target)
        else:
            self._whois(target)

    @text.unicode_to_str
    def _whois(self, targets):
        self.send_raw("WHOIS " + ",".join(targets.replace(',', '').split()))

    @text.unicode_to_str
    def topic(self, channel, new_topic=None):
        if new_topic is None:
            self.send_raw("TOPIC " + channel)
        else:
            self.send_raw("TOPIC %s :%s" % (channel, new_topic))

    @text.unicode_to_str
    def user(self, username, realname):
        self.send_raw("USER %s 0 * :%s" % (username, realname))

    @text.unicode_to_str
    def quit(self, message=""):
        if message == "":
            message = 'SimpBot v' + __version__
        self.send_raw("QUIT" + (message and (" :" + message)))
