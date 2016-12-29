# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

from simpbot.bottools import text
import time


class user:

    def __init__(self, user, host, nick, realname=None, account=None):
        self.user = user
        self.host = host
        self.nick = nick
        self.realname = realname
        self.ircoper = False
        self.account = account
        self.server = None
        self.modes = None
        self.since = None
        self._idle = None
        self.lastmsg = None
        self.ssl = False
        self.completed = False
        self.lines = 0
        self.channels = {}
        self.dateinfo = time.time()

    def __repr__(self):
        return repr("<user '%s'>" % (self.nick if self.nick else '--'))

    @property
    def logged(self):
        return self.account is not None and self.account != ''

    @property
    def nosuch(self):
        return (self.user, self.host, self.realname) == (None, None, None)

    @property
    def tracked(self):
        if self.nosuch:
            return False
        return len(self.channels) != 0

    @property
    def mask(self):
        return '%s!%s@%s' % (self.nick, self.user, self.host)

    @property
    def idle(self):
        return int(time.time()) - self._idle

    def update(self):
        self.dateinfo = int(time.time())

    def uplastmsg(self):
        self.lastmsg = int(time.time())

    def reset(self):
        self.user = None
        self.host = None
        self.realname = None
        self.ircoper = False
        self.account = None
        self.server = None
        self.modes = None
        self.since = None
        self._idle = None
        self.lastmsg = None
        self.ssl = False
        self.completed = False
        self.lines = 0
        self.channels.clear()
        self.update()

    def set(self, attr, value):
        setattr(self, attr, value)
        #self.update()

    def increase_lines(self):
        self.lines += 1
        self.uplastmsg()
        #self.update()

    @text.lower
    def add_channel(self, channame, chanlist):
        if channame in self.channels:
            return
        self.channels[channame] = {'channel': chanlist, 'status': ''}

    @text.lower
    def del_channel(self, channame):
        if not channame in self.channels:
            return
        del self.channels[channame]

    @text.lower
    def get_status(self, channame):
        if channame in self.channels:
            return
        return self.channels[channame]['status']

    def set_status(self, channame, act, status_mode):
        channame = channame.lower()
        #status_mode = status_mode[0]
        if channame in self.channels:
            return
        status = self.channels[channame]['status']

        if act == 'insert':
            if not status_mode in status:
                self.channels[channame]['status'] += status_mode
        elif act == 'remove':
            if status_mode in status:
                self.channels[channame]['status'] = status.replace(status_mode)
        elif act == 'reset':
            self.channels[channame]['status'] = status_mode