# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import time
from threading import Timer
from simpbot.bottools import text
from simpbot.bottools import dummy
from .channels import channel
from .users import user


class manager:

    def __init__(self, irc):
        self.__user_core = {}
        self.__chan_core = {}
        self.irc = irc
        self.check()

        # ajustando sensores #
        self.totaluses = 0
        self.uselimit = 15
        self.maxuse = 20
        self.lastuse = None
        self.ratel = 45
        self.lastmax = None
        self.maxrate = 10
        self.maxstatus = False

    ############################################################################
    #                                CANALES                                   #
    ############################################################################

    @text.lower
    def set_chan(self, chan_name):
        if chan_name in self.__chan_core:
            return
        self.__chan_core[chan_name] = channel(chan_name)

    @text.lower
    def del_chan(self, chan_name):
        if not chan_name in self.__chan_core:
            return
        chan = self.__chan_core[chan_name]
        for usr in chan.users:
            usr.del_channel(chan.channel_name)
        del chan.users[:]
        del self.__chan_core[chan_name]
        del chan

    @text.lower
    def get_chan(self, chan_name):
        if chan_name in self.__chan_core:
            return self.__chan_core[chan_name]

    def chan_list(self):
        return list(self.__chan_core.keys())

    def total_chans(self):
        return len(self.__chan_core)

    ############################################################################
    #                               USUARIOS                                   #
    ############################################################################

    def set_user(self, usr, host, nick, realname=None, account=None):
        lnick = nick.lower()
        if lnick in self.__user_core:
            return self.__user_core[lnick]
        self.__user_core[lnick] = user(usr, host, nick, realname, account)
        return self.__user_core[lnick]

    @text.lower
    def get_user(self, nick):
        if nick in self.__user_core:
            return self.__user_core[nick]

    @text.lower
    def user(self, nick, waitattr='completed', timeout=30):
        status = {'timeout': False}
        timer = None
        if isinstance(timeout, int) or isinstance(timeout, float):
            def timer(dict):
                dict['timeout'] = True
            timer = Timer(timeout, timer, args=[status], kwargs={})
            timer.start()
        while status['timeout'] is not True:
            if nick in self.__user_core:
                user = self.__user_core[nick]
                if getattr(user, waitattr):
                    if timer:
                        timer.cancel()
                    return user
                elif user.nosuch:
                    return
                else:
                    continue
        else:
            raise ValueError

    @text.lower
    def del_user(self, nick):
        if not nick in self.__user_core:
            return

        usr = self.__user_core[nick]
        for chan in list(self.__chan_core.values()):
            chan.remove(usr)
        del self.__user_core[nick]
        del usr

    @text.lower
    def has_user(self, nick):
        return nick in self.__user_core

    def total_users(self):
        return len(self.__user_core)

    def method(self):
        if not self.lastuse:
            self.lastuse = time.time()
        if self.totaluses >= self.uselimit:
            date = int(time.time() - self.lastuse)
            if date <= self.maxrate:
                self.lastuse = time.time()
                #self.lastmax = self.lastuse
                #if not self.maxstatus:
                    #self.wait2end()
                return 'end'
            elif date <= self.ratel:
                return 'who'
            else:
                self.lastuse = time.time()
                self.totaluses = 0
                return 'who'
        else:
            date = int(time.time() - self.lastuse)
            if date >= self.ratel:
                self.lastuse = time.time()
                self.totaluses = 0
            else:
                self.totaluses += 1
            return 'whois'

    def update_nick(self, old_nick, new_nick):
        old_nick = old_nick.lower()
        if old_nick in self.__user_core:
            user = self.__user_core[old_nick]
            del self.__user_core[old_nick]
            user.nick = new_nick
            self.__user_core[new_nick.lower()] = user

    def reset(self):
        if (len(self.__user_core) + len(self.__chan_core)) != 0:
            self.__user_core.clear()
            for chan in list(self.__chan_core.values()):
                del chan.users[:]
            self.__chan_core.clear()

    @dummy.thread
    def check(self):
        while True:
            time.sleep(20)
            if self.irc.connection_status in 'npd':
                continue
            elif self.irc.connection_status == 's':
                break

            date = time.time()
            for usr in list(self.__user_core.values()):
                if usr.tracked:
                    continue
                elif (date - usr.dateinfo) > 30:
                    try:
                        self.del_user(usr.nick)
                    except KeyError:
                        continue

    def who(self, target):
        self.irc._who('{} %chtsunfra,152'.format(target))

    def whois(self, target):
        self.irc._whois(target)

    @dummy.thread
    def wait2end(self, target):
        chan = self.get_chan(target)
        chan.maxstatus = True
        while (time.time() - self.lastuse) >= 5:
            time.sleep(1)
        self.who(target)
        chan.maxstatus = False

    def request(self, nick, channel=None):
        user = self.get_user(nick)
        if user:
            date = int(time.time()) - user.dateinfo
            if user.tracked:
                if date > 3600:
                    user.completed = False
                else:
                    return
            elif date > 20:
                user.completed = False

        if channel is None:
            self.whois(nick)
        else:
            method = self.method()
            if method == 'whois':
                self.whois(nick)
            elif method == 'who':
                self.who(channel)
            elif method == 'end':
                chan = self.get_chan(channel)
                if not chan or chan.maxstatus:
                    return
                self.wait2end()