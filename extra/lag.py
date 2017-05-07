# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import re
import time
import random
import string
import simpbot
from six.moves import _thread
module = simpbot.get_module(sys=True)
loader = module.loader()
regex = re.compile('\001PING (?P<code>.+)\001', re.IGNORECASE)


class lag_handler:

    def __init__(self, expire, tm_chk, max_entries):
        self.lagreq = {}
        self.expire = expire
        self.tm_chk = tm_chk
        self.chk_alive = False
        self.max_entries = max_entries
        self.sep = random.choice(string.punctuation)

    @property
    def status(self):
        return simpbot.modules.has_module(__name__)

    @simpbot.bottools.text.lower
    def hash(self, nick, host):
        return str(hash('%s%s%s' % (nick, self.sep, host))).replace('-', '')

    def send(self, irc, nick, host, target):
        if len(self.lagreq) >= self.max_entries:
            return

        self.set(nick, host, target)
        irc.ctcp('PING', nick, self.hash(nick, host))
        if self.chk_alive:
            return
        else:
            _thread.start_new(self.chk, ())

    def chk(self):
        self.chk_alive = True
        time.sleep(self.tm_chk)
        self.get(None)
        self.chk_alive = False

    def has(self, puke):
        return puke in self.lagreq

    def get(self, puke):
        crt = time.time()
        for _puke, tm in self.lagreq.items():
            if (crt - tm[0]) >= self.expire:
                del self.lagreq[_puke]
        if not self.has(puke):
            return
        else:

            return (round(crt - self.lagreq[puke][0], 2), self.lagreq[puke][1])

    def set(self, nick, host, target):
        self.lagreq[self.hash(nick, host)] = [time.time(), target]


lag_handler = lag_handler((60 * 15), (60 * 15 + 2), 200)


@loader('lag', '(lag!{nickname}?)$',
    #need=['only:channel'],
    i18n={
        'loader': simpbot.localedata.simplocales,
        'module': 'extra.lag',
        'syntax': 'syntax lag',
        'help': 'help lag'})
def lag_ping(irc, ev, result, target, channel, _, locale):
    if _['nickname'] and not _['nickname'].isspace():
        nick = _['nickname'].strip()
        if not irc.request.has_user(nick):
            try: irc.request.user(nick)
            except ValueError: return
        user = irc.request.get_user(nick)

        if user:
            nick = user.nick
            host = user.host
        else:
            return irc.error(target, _(locale['no such nick'], nick=nick))
    else:
        nick = _['user'].nick
        host = _['user'].host
    lag_handler.send(irc, nick, host, target)


@loader('lag-handler', None, need=['only:private,ninja'])
def lang_pong(irc, ev, result, target, channel, _, locale):
    if ev.group('type').upper() != 'NOTICE':
        return

    match = regex.match(ev.group('message'))
    if match is None:
        return

    cod = match.group('code')
    lag = lag_handler.get(cod)
    if lag is None:
        return
    else:
        if cod != lag_handler.hash(*ev.group('nick', 'host')):
            return  # spoof

        irc.msg(lag[1], '%s lag: %ss' % (ev.group('nick'), lag[0]))
        del lag_handler.lagreq[cod]
