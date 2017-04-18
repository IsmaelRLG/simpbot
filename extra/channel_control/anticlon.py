# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)


import simpbot
from . import conf
module = simpbot.get_module(sys=True)
loader = module.loader()


@loader('anti-clon', None)
def anticlon(irc, ev, result, target, channel, _, locale):
    pass

