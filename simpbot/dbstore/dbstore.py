# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import os
import md5
import zlib
from time import time

try:
    import cPickle as pickle
except ImportError:
    import pickle  # lint:ok
from user import user
from channel import channel
from simpbot import envvars
from simpbot.bottools import text
logging = __import__('logging').getLogger('db-store')


class dbstore:

    def __init__(self, network_name, maxc, maxu, rchan, ruser):
        self.name = network_name
        self.__filename = '%s.store' % network_name
        if envvars.dbstore.exists(self.__filename):
            with envvars.dbstore.file(self.__filename, 'r') as store:
                read = store.read()
            if len(read) > 0:
                try:
                    read = zlib.decompress(read)
                    self.__store = pickle.loads(read)
                except Exception as error:
                    logging.error('No se pudo leer "%s": %s', self.name, error)
            self.save()
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
            (md5.new(account + text.randphras()).hexdigest(), int(time()))
        elif type == 'chan':
            chn = account[0].lower()
            usr = account[1].lower()
            hash = md5.new(usr + text.randphras()).hexdigest()  # lint:ok
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
        return md5.new(account).hexdigest()

    @text.lower
    def del_drop(self, type, account):
        if self.has_drop(type, account):
            del self.store_drop[type][md5.new(account).hexdigest()]
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
            self.store_chan[chan_name] = channel(chan_name, int(time()))
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
        for chan_name in list(self.store_chan.keys()):
            chan = self.store_chan[chan_name]
            del self.store_chan[chan_name]
            del chan
        self.save()

    def admins_list(self):
        for user in list(self.store_user.values()):
            if user.isadmin():
                yield user
                continue

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
            text = pickle.dumps(self.__store)
            text = zlib.compress(text)
            store.write(text)