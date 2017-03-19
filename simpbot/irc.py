# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import ssl
import time
import logging
import traceback
import socket

from six import binary_type
from six import string_types
from six import PY3 as python3
from six.moves import _thread
from six.moves import queue

from . import buffer
from . import features
from . import __version__
from .bottools import text
from . import localedata

i18n = localedata.get()
logging = logging.getLogger('IRC')

regexmsg = __import__('re').compile(
    ':(?P<mask>(?P<nick>.+)!(?P<user>.+)@(?P<host>[^ ]+)) '
    '(?P<type>PRIVMSG|NOTICE) (?P<target>[^ ]+) :(?P<message>.+)', 2)


class client:

    def __init__(self, netw, addr, port, nick, user, nickserv=None, sasl=None,
        timeout=240, msgps=.5, wtime=30, servpass=None, prefix='!', lang=None,
        plaintext=False):

        self.connection_status = 'n'
        self.input_alive = False
        self.output_alive = False
        self.lock = False
        self.socket = None
        self.input_buffer = None
        self.output_buffer = queue.Queue()
        self.features = features.FeatureSet()
        self.plaintext = plaintext
        self.default_lang = lang

        self.dbstore = None
        self.request = None
        self.commands = None
        self.autoconnect = False
        self.conf_path = None

        # IRC - Default
        self.servname = netw
        self.addr = addr
        self.ssl = False
        if isinstance(port, string_types):
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
        self.nickserv = nickserv
        self.usens = bool(self.nickserv)
        self.sasl = sasl
        self.timeout = timeout
        self.msgps = msgps
        self.wtime = wtime
        self.prefix = prefix

        if nick == "" or nick[0].isdigit():
            nick = text.randphras(l=7, upper=False, nofd=True)
        if user == "" or user[0].isdigit():
            user = text.randphras(l=7, upper=False, nofd=True)
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
            n: No connected
            c: Connected
            r: Connected and loged
            p: Concection lost
            d: Disconnected
        """
        self.connection_status = modes[0]

    def connect(self, servpass=None, attempts=0):
        if not self.connection_status in 'np':
            return

        attempt = 0
        while attempt <= attempts:
            try:
                self.socket = socket.socket()
                self.socket.settimeout(self.timeout)
                self.input_buffer = buffer.LineBuffer()
                if self.ssl:
                    self.socket = ssl.wrap_socket(self.socket)
                self.socket.connect((self.addr, self.port))
                self.set_status('c')
                break
            except Exception as error:
                logging.error(i18n['connection failure'],
                self.addr, self.port, str(error))
                logging.info(i18n['retrying connect'] % self.wtime)
                time.sleep(self.wtime)
                if attempts == 1:
                    attempt += 2
                elif attempts > 0:
                    attempt += 1
        else:
            return True

        remote_addr = self.socket.getpeername()[0]
        logging.info(i18n['connected'], self.addr, remote_addr, self.port)

        if servpass is not None:
            self.servpass = servpass

        if self.servpass is not None:
            self.passwd(self.servpass)

        if self.nickserv is None:
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
            except queue.Empty:
                if self.connection_status in 'cr':
                    self.set_status('p')
                    self.try_connect()

            if text == 0:
                break

            if isinstance(text, string_types):
                if python3:
                    message = text.encode() + b'\r\n'
                else:
                    message = text + '\r\n'
            else:
                logging.warning(i18n['invalid message'])
                continue

            if len(text) > 512:
                logging.warrning(i18n['invalid message size'])
                continue

            try:
                self.socket.send(message)
            except socket.error:
                if self.connection_status in 'cr':
                    self.set_status('p')
                    self.try_connect()

            if self.plaintext:
                logging.info(i18n['output'], self.servname, text)
            time.sleep(self.msgps)
        else:
            self.input_alive = False

    def input(self):
        while self.connection_status in 'crp':
            self.input_alive = True
            try:
                recv = self.socket.recv(1024)
            except socket.timeout:
                logging.error(i18n['connection timeout'],
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
                if python3 and isinstance(line, binary_type):
                    line = str(line, 'utf-8')
                if not line:
                    continue
                if self.plaintext:
                    logging.info(i18n['input'], self.servname, line)
                msg = regexmsg.match(line)
                if msg and self.commands:
                    self.commands.put(msg)
                    continue

                self.proccess_handlers(line)
        else:
            self.input_alive = False

    def try_connect(self, attempts=0):
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
        if self.connect(attempts=attempts):
            self.lock = False
            return False
        #except KeyboardInterrupt:
         #   self.lock = False
         #   return

        if not self.input_alive:
            _thread.start_new(self.input, (), {})
        if not self.output_alive:
            _thread.start_new(self.output, (), {})
        else:
            while not self.output_buffer.empty():
                self.output_buffer.get()

        self.login()
        self.lock = False

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
        if self.connection_status in 'npds':
            return
        self.output_buffer.put(text)

    ##########################################################################
    #                             Comandos IRC                               #
    ##########################################################################

    @text.normalize
    def ctcp(self, ctcptype, target, parameter=""):
        tmpl = (
            "\001{ctcptype} {parameter}\001" if parameter else
            "\001{ctcptype}\001"
        )
        self.privmsg(target, tmpl.format(**vars()))

    @text.normalize
    def ctcp_reply(self, target, parameter):
        self.notice(target, "\001%s\001" % parameter)

    @text.normalize
    def join(self, channel, key=""):
        self.send_raw("JOIN %s%s" % (channel, (key and (" " + key))))

    @text.normalize
    def kick(self, channel, nick, comment=""):
        tmpl = "KICK {channel} {nick}"
        if comment:
            tmpl += " :{comment}"
        self.send_raw(tmpl.format(**vars()))

    @text.normalize
    def invite(self, nick, channel):
        self.send_raw(" ".join(["INVITE", nick, channel]).strip())

    @text.normalize
    def nick(self, newnick):
        self.send_raw("NICK " + newnick)

    @text.normalize
    def notice(self, target, msg):
        for line in text.part(msg, 256):
            self.send_raw("NOTICE %s :%s" % (target, line))

    @text.normalize
    def part(self, channels, message=""):
        self.send_raw("PART %s%s" % (channels, (message and (" " + message))))

    @text.normalize
    def privmsg(self, target, msg):
        for line in text.part(msg, 256):
            self.send_raw("PRIVMSG %s :%s" % (target, line))

    @text.normalize
    def msg(self, target, text):
        self.notice(target, text)

    @text.normalize
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

        for target in ison:
            self.notice(target, text)

    @text.normalize
    def error(self, target, msg):
        for line in text.part(msg, 256, '... '):
            self.send_raw("NOTICE %s :[ERROR]: %s" % (target, line))

    @text.normalize
    def passwd(self, password):
        self.send_raw("PASS " + password)

    def pong(self, target, target2=""):
        self.send_raw("PONG %s%s" % (target, target2 and (" " + target2)))

    @text.normalize
    def remove(self, channel, nick, comment=""):
        tmpl = "REMOVE {channel} {nick}"
        if comment:
            tmpl += " :{comment}"
        self.send_raw(tmpl.format(**vars()))

    def who(self, target):
        if self.request:
            self.request.who(target)
        else:
            self._who(target)

    @text.normalize
    def _who(self, target="", op=""):
        self.send_raw("WHO%s%s" % (target and (" " + target), op and (" o")))

    def whois(self, target):
        if self.request:
            self.request.whois(target)
        else:
            self._whois(target)

    @text.normalize
    def _whois(self, targets):
        self.send_raw("WHOIS " + ",".join(targets.replace(',', '').split()))

    @text.normalize
    def topic(self, channel, new_topic=None):
        if new_topic is None:
            self.send_raw("TOPIC " + channel)
        else:
            self.send_raw("TOPIC %s :%s" % (channel, new_topic))

    @text.normalize
    def user(self, username, realname):
        self.send_raw("USER %s 0 * :%s" % (username, realname))

    @text.normalize
    def quit(self, message=""):
        if message == "":
            message = 'SimpBot v' + __version__
        self.send_raw("QUIT" + (message and (" :" + message)))
