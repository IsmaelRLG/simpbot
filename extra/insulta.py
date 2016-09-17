# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot
import random


@simpbot.commands.addCommand('insulta !{nick}', 'insulta a alguien', 'insulta')
def test(irc, ev, result, target, channel, _):
    txt = simpbot.envvars.data.file('insulta.txt', 'a+')
    lines = txt.readlines()
    if len(lines) == 0:
        lines = ['eres idiota!']
    _['insulto'] = random.choice(lines)
    irc.msg(target, _('{nick}: {insulto}'))
