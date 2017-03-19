# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import os
import sys
import simpbot

current_mod = sys.modules[__name__]
current_dir = os.path.dirname(__file__)
simpbot.modules.path.append(current_dir)
for filordir in os.listdir(current_dir):
    try:
        module = simpbot.modules.load_module(filordir, addmod=False, trace=True)
    except ImportError:
        continue

    # if any error occurred, it will end here
    if isinstance(module, Exception):
        continue
    setattr(current_mod, module.__name__, module)