# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import simpbot
module = simpbot.get_module(sys=True)
loader = module.loader()


@loader('ping', 'ping', syntax='ping', help="ping -> pong!")
def ping(irc, ev, result, target, channel, _, locale):
    irc.msg(target, _('{user.nick}: pong'))
