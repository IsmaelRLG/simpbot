# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot


@simpbot.commands.addCommand('nick !{new_nick}', 'Cambia de nick', 'nick')
@simpbot.commands.admin
def chnick(irc, ev, result, target, channel, _):
    irc.nick(_['new_nick'])