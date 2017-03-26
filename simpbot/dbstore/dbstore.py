# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)
from __future__ import unicode_literals

import os
import sys
import zlib
import base64
import hashlib

from time import time
from .user import user
from .channel import channel
from simpbot import envvars
from simpbot.bottools import text
from six.moves import cPickle
logging = __import__('logging').getLogger('db-store')

if sys.version_info.major == 3:
    modes = 'rb'
else:
    modes = 'r'


class dbstore:

    def __init__(self, network_name, maxc, maxu, rchan, ruser):
        self.name = network_name
        self.__filename = '%s.store' % network_name
        if envvars.dbstore.exists(self.__filename):
            with envvars.dbstore.file(self.__filename, modes) as store:
                read = store.read()
            if len(read) > 0:
                try:
                    read = base64.b64decode(read)
                    read = zlib.decompress(read)
                    self.__store = cPickle.loads(read)
                except Exception as error:
                    logging.error('No se pudo leer "%s": %s', self.name, error)
                    return
            else:
                self.__store = self.base_dict()
        else:
            self.__store = self.base_dict()
        self.max_channels = maxc
        self.max_users = maxu
        self.chanregister = rchan
        self.userregister = ruser

    def base_dict(self):
        return {'user': {}, 'chan': {}, 'task': {
               'request': {'user': {}, 'chan': {}},
               'drop': {'user': {}, 'chan': {}}}}

    @property
    def store_user(self):
        return self.__store['user']

    @property
    def store_chan(self):
        return self.__store['chan']

    @property
    def store_task(self):
        return self.__store['task']

    @property
    def store_request(self):
        return self.store_task['request']

    @property
    def store_drop(self):
        return self.store_task['drop']

    @text.lower
    def request(self, type, account):
        if type == 'user':
            self.store_request[type][account] =\
            (hashlib.md5(account + text.randphras()).hexdigest(), int(time()))
        elif type == 'chan':
            chn = account[0].lower()
            usr = account[1].lower()
            hash = hashlib.md5(usr + text.randphras()).hexdigest()  # lint:ok
            self.store_request[type][chn] = (hash, usr, int(time()))
        self.save()

    @text.lower
    def get_request(self, type, account):
        if self.has_request(type, account):
            return self.store_request[type][account]

    @text.lower
    def del_request(self, type, account):
        if self.has_request(type, account):
            del self.store_request[type][account]
            self.save()

    @text.lower
    def has_request(self, type, account):
        return account in self.store_request[type]

    @text.lower
    def drop(self, type, account):
        hash = md5.new(account).hexdigest()  # lint:ok
        self.store_drop[type][hash] = int(time())
        self.save()
        return hash

    @text.lower
    def get_hashdrop(self, account):
        return hashlib.md5(account).hexdigest()

    @text.lower
    def del_drop(self, type, account):
        if self.has_drop(type, account):
            del self.store_drop[type][hashlib.md5(account).hexdigest()]
            self.save()

    @text.lower
    def has_drop(self, type, account):
        hash = md5.new(account).hexdigest()  # lint:ok
        if hash in self.store_drop[type]:
            date = self.store_drop[type][hash]
            if (time() - date) >= (60 * 60 * 24):
                return False
            else:
                return True
        else:
            return False

    @text.lower
    def register_chan(self, chan_name):
        if not self.has_chan(chan_name):
            date = int(time())
            self.store_chan[chan_name] = channel(self.name, chan_name, date)
            self.save()

    @text.lower
    def register_user(self, account):
        if self.has_user(account):
            return

        self.store_user[account] = user(self.name, account, int(time()), None)
        self.save()

    @text.lower
    def get_chan(self, chan_name):
        if self.has_chan(chan_name):
            return self.store_chan[chan_name]

    @text.lower
    def get_user(self, account):
        if self.has_user(account):
            return self.store_user[account]

    @text.lower
    def has_chan(self, chan_name):
        return chan_name in self.store_chan

    @text.lower
    def has_user(self, account):
        return account in self.store_user

    @text.lower
    def drop_chan(self, chan_name):
        if self.has_chan(chan_name):
            chan = self.store_chan[chan_name]
            del self.store_chan[chan_name]
            del chan
            self.save()

    @text.lower
    def drop_user(self, account):
        if self.has_user(account):
            _account = self.store_user[account]
            del self.store_user[account]
            del _account
            self.save()

    def reset(self):
        self.__store.clear()
        self.__store.update(self.base_dict())
        self.save()

    def reset_chans(self):
        for chan_name in self.store_chan.keys():
            chan = self.store_chan[chan_name]
            del self.store_chan[chan_name]
            del chan
        self.save()

    def admins_list(self):
        for user in self.store_user.values():
            if user.isadmin():
                yield user

    def total_chan(self):
        return len(self.store_chan)

    def total_user(self):
        return len(self.store_user)

    def save(self):
        if self.total_chan() == 0 and self.total_user() == 0:
            if envvars.dbstore.exists(self.__filename):
                os.remove(envvars.dbstore.join(self.__filename))
            return

        with envvars.dbstore.file(self.__filename, 'w') as store:
            text = cPickle.dumps(self.__store)
            text = zlib.compress(text)
            text = base64.b64encode(text)
            if sys.version_info.major == 3:
                text = text.decode()
            store.write(text)