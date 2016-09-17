# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot


@simpbot.commands.addCommand('nick !{new_nick}', 'Cambia de nick', 'nick')
@simpbot.commands.admin