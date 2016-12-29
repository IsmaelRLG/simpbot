# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)


import re
from simpbot import mode
from simpbot.bottools import irc


class channel:

    def __init__(self, channel, registered, flags={}):
        self.channel = channel
        self.registered = registered
        self.flags = flags
        self.key = None
        self.verbose = False
        self.template = {
            'founder': 'FOVbfiklmorstv',
            'admin': 'OVbfiklmorstv',
            'op': 'Vbiklmotv',
            'voice': 'Viltv',
            'clear': ''}

    def __del__(self):
        self.drop()

    def get_mask(self, mask):
        if not irc.valid_mask(mask):
            return

        finded = False
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
        if isinstance(account, basestring):
            account = self.get_mask(account)
            if not account:
                return
        if account in self.flags:
            return self.flags[account]

    def set_flags(self, account, flags, dadd='', ddel=''):
        simpaccount = True
        if isinstance(account, basestring):
            account = self.get_mask(account)
            if account:
                simpaccount = False
            else:
                return

        if account in self.flags:
            initflags = self.flags[account]
        else:
            initflags = None

        print('%s in %s' % (flags, flags.lower() in self.template.keys()))
        if flags.lower() in self.template:
            if not simpaccount:
                for l in self.template[flags.lower()]:
                    if not l in 'Ffs':
                        continue
                    return

            flags = [self.template[flags.lower()]]
            for l in dadd:
                flags.append(flags.pop().replace(l, ''))
            flags = flags[0]

            if initflags:
                for l in initflags:
                    if l in ddel and not l in flags:
                        flags += l

        elif '+' in flags or '-' in flags:
            new_flags = []
            if initflags:
                new_flags = [l for l in initflags]

            for sign, l, n in mode._parse_modes(flags, only='FOVbfiklmorstv'):
                if sign == '+' and not l in new_flags:
                    if l in dadd:
                        continue
                    elif not simpaccount and l in 'Ffs':
                        continue
                    new_flags.append(l)
                elif sign == '-' and l in new_flags:
                    if l in ddel:
                        continue
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
            flags = [l for l in flags]
            flags.sort()
            flags = ''.join(flags)
            if flags != initflags:
                self.flags[account] = flags
                if simpaccount:
                    account.add_chan(self)
            else:
                initflags = None
                flags = None

        # Retorna los cambios
        return initflags, flags

    def has_flags(self, account):
        if isinstance(account, basestring):
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
        if isinstance(account, basestring):
            account = self.get_mask(account)
            if not account:
                return

        if account in self.flags:
            del self.flags[account]
            account.del_chan(self)