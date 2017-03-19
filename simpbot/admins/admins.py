# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)
from __future__ import unicode_literals

from simpbot import control
from hashlib import new
from . import capab


class admins(control.control):

    def __init__(self, network, user, hash, algm, logins, maxlogins, ison, conf,
        path, timeout, verbose, account):
        super(admins, self).__init__('.'.join(['simpbot-admin',
            'global' if network is None else network, user]))
        self.network = network
        self.user = user
        self.__password = hash
        self.logins = logins
        self.maxlogins = maxlogins
        self.timeout = timeout
        self.verbose = verbose
        self.capab = []
        self.hash_algorithm = algm
        self.conf = conf
        self.ison = ison
        self.account = account
        self.confpath = path

    def __repr__(self):
        if self.network:
            network = 'network=%s' % self.network
        else:
            network = 'global'
        return '<admin %s %s>' % (network, self.user)

    def __str__(self):
        network = 'local ' + self.network if self.network else 'global'
        return '%s %s' % (network, self.user)

    def isglobal(self):
        return self.network is None

    def checkpass(self, password):
        return self.hash(password) == self.__password

    def hash(self, text):
        return new(self.hash_algorithm, text.encode('utf-8')).hexdigest()

    def has_maxlogin(self):
        if self.maxlogins == 0:
            return False
        else:
            return self.logins == self.maxlogins

    def logged(self):
        return self.logins > 0

    def update_password(self, new_pass):
        self.__password = self.hash(new_pass)
        self.save()

    def set_capab(self, capability):
        if capab.exists(capability) and not self.has_capab(capability):
            self.capab.append(capability)

    def del_capab(self, capability):
        if self.has_capab(capability):
            self.capab.remove(capability)

    def has_capab(self, capability):
        return capability in self.capab

    def save(self):
        if self.conf is None or self.confpath is None:
            return

        equal = lambda boolean: 'yes' if boolean else 'no'
        admin = self.__str__()

        if not self.conf.has_section(admin):
            self.conf.add_section(admin)

        self.conf.set(admin, 'password', self.__password)
        self.conf.set(admin, 'timeout', str(self.timeout))
        self.conf.set(admin, 'maxlogins', str(self.maxlogins))
        self.conf.set(admin, 'verbose', equal(self.verbose))
        self.conf.set(admin, 'capability', ','.join(self.capab))
        self.conf.set(admin, 'isonick', ','.join(self.ison))
        if self.logins > 0:
            self.conf.set(admin, 'logins', str(self.logins))
        if self.hash_algorithm != 'md5':
            self.conf.set(admin, 'hash_algorithm', self.hash_algorithm)

        with file(self.confpath, 'w') as cfg:
            self.conf.write(cfg)