# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot
from os import system
from time import sleep


@simpbot.commands.addCommand('(shutdown|stop|apagar)!{mensaje}+?',
    'Apaga el bot remotamente.', 'shutdown')
@simpbot.commands.admin
def shutdown(irc, ev, result, target, channel, _):
    irc.verbose(_('Orden de apagado enviada por: {mask}'))
    irc.verbose('Apagando en diez (10) segundos...')
    sleep(10)
    if _['mensaje'] == None:
        _['mensaje'] = 'SimpBot v' + simpbot.__version__
    irc.quit(_('APAGADO: {mensaje}'))
    sleep(2)
    system('simpbot -a stop')