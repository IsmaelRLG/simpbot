# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)


class channel:

    def __init__(self, channel_name):
        self.channel_name = channel_name
        self.maxstatus = False
        self.users = []

    def __iter__(self):
        return iter(self.users)

    def __len(self):
        return len(self.users)

    def append(self, user):
        if not user in self.users:
            self.users.append(user)
            user.add_channel(self.channel_name, self)

    def remove(self, user):
        if user in self.users:
            self.users.remove(user)
        user.del_channel(self.channel_name)

    def has_user(self, user):
        return user in self.users

    def search(self, tofind, attr='mask', method='find'):
        if not hasattr(self, attr):
            return
        result = []
        for data in self.users:
            attr = getattr(data, attr)
            if attr is None:
                continue
            elif method == 'comp':
                if attr.lower() == tofind.lower():
                    result.append(data)
                    continue
                else:
                    continue
            elif method == 'find':
                if attr.find(tofind) != -1:
                    result.append(data)
                    continue
                else:
                    continue
        return result

    def get_user(self, nickname):
        for user in self.users:
            if user.nick.lower() == nickname.lower():
                return user
