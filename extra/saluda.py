# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot
import random


@simpbot.commands.addCommand('saluda !{nick}', 'Saluda a un usuario', 'saluda')
def test(irc, ev, result, target, channel, _):
    txt = simpbot.envvars.data.file('saluda.txt', 'a+')
    lines = txt.readlines()
    if len(lines) == 0:
        lines = ['Hola :D']
    _['saludo'] = random.choice(lines)
    irc.msg(target, _('{nickname}: {saludo}'))
