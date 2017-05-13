# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)
#
# Simpcoins! inspired by buttcoins
#---------------------------------

import hashlib, random, datetime
from time import time
from . import config
from .database import User, Dealings
from hashlib import new


class bank:

    def __init__(self, network):
        self.network = network.lower()
        self.usermap = {}
        self.on_load()

        try:
            self.bot_acc = User.get(User.id == self.genid(config.bot_account))
        except:
            self.bot_acc = self.create(config.bot_account)

    def __getitem__(self, account):
        user_id = self.genid(account)
        if not self.has_user(user_id):
            try:
                user = User.get(User.id == user_id)
            except User.DoesNotExist:
                return

            self.usermap[user.id] = user
            return user
        else:
            return self.usermap[user_id]

    def __iter__(self):
        return iter(self.usermap)

    def has_user(self, user_id):
        return user_id in self.usermap

    def get(self, account):
        return self.__getitem__(account)

    def create(self, account, d=True):
        user = User.create(id=self.genid(account), username=account, decrease=d)
        self.usermap[user.id] = user
        return user

    def on_load(self):
        for user in User.select().where(User.network == self.network):
            self.usermap[user.id] = user

    def genid(self, account):
        return new('md5', '%s %s' % (account.lower(), self.network)).hexdigest()

    def transfer(self, From, To, amount, decrease=True):
        if From.decrease is True and decrease:
            if From.coins < amount:
                return
            else:
                From.coins -= amount
                From.save()

        tr_code = self.gen_trcode()
        To.coins += amount
        To.save()
        Dealings.create(id=tr_code, from_user=From, to_user=To, amount=amount)
        return tr_code

    def gen_trcode(self):
        return hashlib.new(config.hash_function, '%f' % time()).hexdigest()[:8]

    def increase_lines(self, user):
        user.lines += 1
        user.last_seen = datetime.datetime.now()
        if user.lines > user.levelup:
            user.levelup += ((config.p_increase * user.levelup) / 100)
            user.chances += 1

        # building the block...
        for chance in range(user.chances):
            char = random.choice(config.slct_block)
            if not char in config.full_block or char in user.c_block:
                continue
            else:
                user.c_block += char
                break

        if len(user.c_block) == len(config.full_block):
            # block built
            user.c_block = ''
            self.transfer(self.bot_acc, user, config.default_ecoins)
        else:
            user.save()


stack = {}


def dispatch(network):
    if not network in stack:
        stack[network] = bank(network)
    return stack[network]