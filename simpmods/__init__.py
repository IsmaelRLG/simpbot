# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import os
import re
import sys
import simpbot

current_mod = sys.modules[__name__]
current_dir = os.path.dirname(__file__)
simpbot.modules.path.append(current_dir)
r_ext = ['py']
i_ext = ['pyc', 'pyo']
i_fil = ['__init__']
a_ext = i_ext + r_ext

regex = re.compile('(?P<filename>.+)(?P<f_ext>\.(?P<ext>%s))' % '|'.join(a_ext))
for pymod in os.listdir(current_dir):
    if os.path.isfile(os.path.join(current_dir, pymod)):
        res = regex.match(pymod)
        if res is None or res.group('ext') in i_ext:
            continue
        if res.group('filename') in i_fil:
            continue
        pymod = pymod.replace(res.group('f_ext'), '')

    try:
        module = simpbot.modules.load_module(pymod, addmod=False, trace=True)
    except Exception as error:
        continue

    # if any error occurred, it will end here
    if isinstance(module, Exception):
        continue
    setattr(current_mod, module.__name__, module)