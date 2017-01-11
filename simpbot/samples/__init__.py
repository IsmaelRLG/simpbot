# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

from simpbot import bottools

#lint:disable
from . import server
from . import admins
#lint:enable


def savecfg(name, path):
    with file(path, 'w') as fp:
        sample = eval(name).sample
        if sample.startswith('\n', ''):
            sample = sample.replace('\n', '', 1)
        fp.write(bottools.dummy())
        fp.write(sample)