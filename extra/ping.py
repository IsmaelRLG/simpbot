# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot


@simpbot.commands.addCommand('ping', 'PING -> PONG', 'ping')
def ping(irc, ev, result, target, channel, _):
    irc.msg(target, _('{nickname}: pong'))
