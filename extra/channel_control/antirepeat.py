# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)


import simpbot
from . import conf
module = simpbot.get_module(sys=True)
loader = module.loader()


@loader('anti-repeat', None,
    need={'only:channel', 'registered chan:non-channel'},
    i18n={'loader': simpbot.localedata.simplocales})
def antirepeat(irc, ev, result, target, channel, _, locale):
    if not irc.servname in conf.repeat:
        return
    if not channel.lower() in conf.repeat[irc.servname]:
        return
    if conf.in_whitelist(conf.wl_repeat, irc, _['user'], channel):
        return
