# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import re
import os
import imp
import sys as sys_
import logging
from . import module
from simpbot import control
from simpbot.envvars import modules
from simpbot.envvars import coremodules
from simpbot.workarea import workarea
refile = re.compile('(?P<name>.+)\.(?P<ext>py[co]?$)', re.IGNORECASE)
logging = logging.getLogger('coremod')
from simpbot import localedata

i18n = localedata.get()


class coremod(control.control):
    def __init__(self, path=None):
        self.core = coremodules
        if path is None:
            self.path = modules
        else:
            self.path = workarea(path)
            if self.path is None:
                return
        super(coremod, self).__init__('global.simpbot.modules')

    def __iter__(self):
        return iter(list(self.core.items()))

    def find_module(self, modname):
        pydata = []
        sub = []
        abspath = self.path.join(modname)
        if not self.path.exists(modname):
            logging.error(i18n['module no exists'], abspath)
            return
        elif self.path.isfile(modname):
            rmatch = refile(modname)
            if rmatch is None:
                logging.error(i18n['no python code'], abspath)
                return
            ext = rmatch.group('ext').lower()
            nam = rmatch.group('name')
            lvl = {'py': 1, 'pyc': 2}
            mod = {'py': 'U', 'pyc': 'rb'}
            if ext in lvl:
                lvl = lvl[ext]
                mod = mod[ext]
            else:
                return

            pydata.append(self.path.open(modname, ext))
            sub.extend(['.' + ext, ext, lvl])
        elif self.path.isdir(modname):
            initp = self.path.join(modname, '__init__.py')
            initb = self.path.join(modname, '__init__.pyc')
            if not self.path.exists(initp) or not self.path.exists(initb):
                logging.error(i18n['no python code'], abspath)
                return
            elif self.path.isdir(initp) or self.path.isdir(initb):
                logging.error(i18n['is a directory'], abspath)
                return
            else:
                nam = os.path.basename(modname)
            pydata.append(None)
            sub.extend(['', '', 5])
        else:
            logging.warning(i18n['symbolic link'], abspath)
            return
        pydata.append(modname)
        pydata.append(tuple(sub))
        final = [nam]
        final.extend(pydata)
        return tuple(final)

    def load_module(self, modname, addmod=True, return_mod=True):
        data = self.find_module(modname)
        if data is None:
            return
        logging.debug(i18n['trying load'], modname)
        try:
            mod = imp.load_module(*data)
        except Exception as error:
            logging.error(i18n['module with errors'], data[0], error)
            return error
        else:
            logging.info(i18n['module loaded'], data[0])
        if addmod:
            simmod = self.get_module(modname)
            simmod.load_meta(mod)
        if return_mod:
            return mod

    @staticmethod
    def download_module(modname):
        if modname in coremodules:
            coremodules[modname].reset()
            del coremodules[modname]
            return True
        else:
            return False

    @staticmethod
    def reload_module(modname):
        if modname in coremodules:
            mod = coremodules[modname]
            if mod.rechargable():
                mod.reload()
                return True
        return False

    @staticmethod
    def get_module(modname=None, sys=False):
        if modname is None:
            modname = sys_._getframe(1).f_globals['__name__']
        if modname in coremodules:
            return coremodules[modname]
        else:
            mod = module.module(modname)
            if sys:
                if modname in sys_.modules:
                    mod.load_meta(sys_.modules[modname])
            coremodules[modname] = mod
            return mod

    @staticmethod
    def del_module(modname):
        if modname in coremodules:
            mod = coremodules[modname]
            if mod.__class__ is module.module:
                if len(mod) > 0:
                    mod.reset()
            del coremodules[modname]
            del mod
            return True
        else:
            return False

    @staticmethod
    def has_module(modname):
        return modname in coremodules
