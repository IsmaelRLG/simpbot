# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import os
import shutil
import mimetypes

from shutil import move  # lint:ok


def rm(path):
    method = os.remove
    if os.path.isdir(path):
        method = shutil.rmtree
    method(path)


def copy(src, dst):
    method = shutil.copy2
    if os.path.isdir(dst):
        method = shutil.copytree
    method(src, dst)


def mimetype(path):
    return mimetypes.guess_type(path)
