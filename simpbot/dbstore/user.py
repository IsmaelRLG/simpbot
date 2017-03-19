# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import time
from simpbot import envvars
from simpbot import localedata


class user(object):

    def __init__(self, net, user, since, status, admin=None, logindate=None):
        self.network = net
        self.chan_flags = []
        self.username = user
        self.since = since
        self._admin = admin
        self._lang = None
        self.logindate = logindate
        self.status = status
        if self.isadmin():
            self.admin.logins.append(self)

    def __del__(self):
        self.drop()

    def __repr__(self):
        return repr("<user: %s>" % self.username)

    def add_chan(self, chan):
        if not chan in self.chan_flags:
            self.chan_flags.append(chan)

    def del_chan(self, chan):
        if chan in self.chan_flags:
            self.chan_flags.remove(chan)

    def drop(self):
        self.set_admin(None, None)
        for channel in self.chan_flags:
            if channel.has_flags(self.username):
                channel.remove(self.username)
        del self.chan_flags[:]

    def locked(self):
        return self.status is not None

    def lock(self, reason, admin_mask, admin_name):
        self.status = (reason, int(time.time()), admin_mask, admin_name)

    def unlock(self):
        self.status = None

    def isadmin(self):
        if self._admin is not None and self._admin in envvars.admins:
            admin = envvars.admins[self._admin]
            if admin.timeout == 0:
                return True
            elif (int(time.time()) - self.logindate) > admin.timeout:
                self._admin = None
                self._logindate = None
                if admin.logins > 0:
                    admin.logins -= 1
                    admin.save()
                return False
            else:
                return True
        else:
            return False

    @property
    def admin(self):
        if self.isadmin():
            return envvars.admins[self._admin]

    @property
    def lang(self):
        if self._lang is None:
            if self.network in envvars.networks:
                return envvars.networks[self.network].default_lang
            else:
                # wtf? really?
                return envvars.default_lang
        else:
            self._lang

    def set_lang(self, lang):
        if localedata.simplocales.exists(lang, 'fullsupport'):
            self._lang = lang

    def set_admin(self, admin, logindate):
        if admin is None:
            self._admin = None
            self.logindate = None
            if self.isadmin():
                _admin = envvars.admins[self._admin]
                if self in _admin.logins:
                    _admin.logins.remove(self)
        elif admin in envvars.admins:
            _admin = envvars.admins[admin]
            _admin.logins += 1
            _admin.save()
            self._admin = admin
            self.logindate = logindate
