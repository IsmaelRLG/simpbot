# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import re
from simpbot import mode
from simpbot import envvars
from simpbot.bottools import irc
from six import string_types


class channel:

    def __init__(self, network, channel, date, flags={}):
        self.network = network
        self.channel = channel
        self.date = date
        self.flags = flags
        self.key = None
        self.verbose = False
        self.template = {
            'founder': 'BFOVbfiklmorstv',
            'admin': 'BOVbfiklmorstv',
            'op': 'BOVbiklmotv',
            'voice': 'Viltv',
            'clear': ''}
        self._lang = None

    @property
    def lang(self):
        if self._lang is None:
            if self.network in envvars.networks:
                return envvars.networks[self.network].default_lang
            else:
                # wtf? really?
                return envvars.default_lang
        else:
            return self._lang

    def set_lang(self, lang):
        self._lang = lang

    def __del__(self):
        self.drop()

    def get_mask(self, mask):
        if not irc.valid_mask(mask):
            return None
        finded = None
        for key in self.flags.keys():
            # Buscamos compilados...
            if isinstance(key, tuple):
                # Se encontró uno :O
                if key[1] == mask or key[0].match(mask):
                    mask = key
                    finded = True
                    break

        if not finded:
            mask = (re.compile(irc.parse_mask(mask), re.IGNORECASE), mask)
        return mask

    def set_key(self, key):
        self.key = key

    def get_flags(self, account):
        if isinstance(account, string_types):
            account = self.get_mask(account)
            if not account:
                return
        if account in self.flags:
            return self.flags[account]

    def set_flags(self, account, flags, dadd='', ddel=''):
        simpaccount = True
        if isinstance(account, string_types):
            account = self.get_mask(account)
            if account:
                simpaccount = False
            else:
                return
        if account in self.flags:
            initflags = self.flags[account]
        else:
            initflags = None

        if flags.lower() in self.template:
            if not simpaccount:
                for l in self.template[flags.lower()]:
                    if l not in 'Ffs':
                        continue
                    return

            flags = [self.template[flags.lower()]]
            for l in dadd:
                flags.append(flags.pop().replace(l, ''))

            flags = flags[0]
            if initflags:
                for l in initflags:
                    if l in ddel and l not in flags:
                        flags += l
                        continue
        elif '+' in flags or '-' in flags:
            new_flags = [] if initflags else list(initflags)

            for sign, l, n in mode._parse_modes(flags, only='BFOVbfiklmorstv'):
                if sign == '+' and not l in new_flags:
                    if l in dadd:
                        continue
                    elif not simpaccount and l in 'Ffs':
                        continue
                    new_flags.append(l)
                    continue
                elif sign == '-' and l in new_flags and not l in ddel:
                    new_flags.remove(l)

            new_flags.sort()
            flags = ''.join(new_flags)
        else:
            return

        if len(flags) == 0:
            if initflags:
                del self.flags[account]
                if simpaccount:
                    account.del_chan(self)
            flags = None
        else:
            flags = list(flags)
            flags.sort()
            flags = ''.join(flags)
            if flags != initflags:
                self.flags[account] = flags
                if simpaccount:
                    account.add_chan(self)
            else:
                initflags = None
                flags = None

        return (initflags, flags)

    def has_flags(self, account):
        if isinstance(account, string_types):
            account = self.get_mask(account)
            if not account:
                return
        return account in self.flags

    def drop(self):
        for account in self.flags.keys():
            del self.flags[account]
            if isinstance(account, tuple):
                continue
            account.del_chan(self)

    def remove(self, account):
        if isinstance(account, string_types):
            account = self.get_mask(account)
            if not account:
                return
        if account in self.flags:
            del self.flags[account]
            account.del_chan(self)
