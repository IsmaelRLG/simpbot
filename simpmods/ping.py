# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot
module = simpbot.get_module(sys=True)
loader = module.loader()


@loader('ping', 'ping', syntax='ping')
def ping(irc, ev, result, target, channel, _):
    """Al «PING» se responde «PONG»."""
    irc.msg(target, _('{nick}: pong'))
