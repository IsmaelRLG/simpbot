# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot
import random
eightball = simpbot.envvars.data.new_wa('eightball')


@simpbot.commands.addCommand('dime !{msg}+', 'responde una pregunta', 'dime')
def dime(irc, ev, result, target, channel, _):
    # Archivos de respuesta
    neg = eightball.file('negativo.txt', 'a+')
    neu = eightball.file('neutral.txt', 'a+')
    pos = eightball.file('positivo.txt', 'a+')

    def default(openf, default_line):
        lines = openf.readlines()
        openf.close()
        if len(lines) == 0:
            lines = [default_line]
        return lines

    responses = {
        'neg': default(neg, 'No'),
        'neu': default(neu, 'No sé'),
        'pos': default(pos, 'Sí')
    }

    _['respuesta'] = random.choice(responses[random.choice(responses.keys())])
    irc.msg(target, _('{nickname}: {respuesta}'))