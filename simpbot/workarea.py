# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import os
from . import functools


class workarea:
    def __init__(self, abspath, check=True, extra=None):
        self.abspath = abspath
        if not os.path.exists(self.abspath) and check:
            os.mkdir(self.abspath)
            self.first_commit = True
        elif os.path.isfile(self.abspath) or os.path.islink(self.abspath):
            return

        if extra and check:
            for type, content in extra.items():
                if type == 'files':
                    for filename in content:
                        if not self.exists(filename):
                            self.file(filename, 'a')
                    continue
                if type == 'dirs':
                    for dirname in content:
                        if not self.exists(dirname):
                            self.file(dirname, 'a')

    def file(self, filename, mode):
        return file(self.join(filename), mode)

    def exists(self, path):
        return os.path.exists(self.join(path))

    def isfile(self, path):
        return os.path.isfile(self.join(path))

    def islink(self, path):
        return os.path.islink(self.join(path))

    def isdir(self, path):
        return os.path.isdir(self.join(path))

    def rm(self, path):
        functools.rm(path)

    def join(self, *args):
        return os.path.join(self.abspath, *args)

    def listdir(self, path=None):
        return os.listdir(self.join(path) if path else self.abspath)

    def mkdir(self, folder):
        os.mkdir(self.join(folder))

    def touch(self, filename):
        self.file(filename, 'w').close()

    def copy(self, src, dst):
        functools.copy(src, dst)

    def move(self, src, dst):
        functools.move(src, dst)

    def new_wa(self, dirname, *args, **kwargs):
        wa = workarea(self.join(dirname), *args, **kwargs)
        wa.main = self
        if hasattr(self, 'level'):
            wa.level = self.level + 1
        else:
            wa.level = 1

        return wa

    def rename(self, old, new):
        os.rename(old, new)

    def mimetype(self, filename):
        return functools.mimetype(self.join(filename))

#    def if_first_commit(self, text2write):
