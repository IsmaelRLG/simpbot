# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import re
import imp
import sys as sys_
import logging
import traceback
from . import module
from simpbot import control
from simpbot.envvars import mods_path
from simpbot.envvars import coremodules
refile = re.compile('(?P<name>.+)\.(?P<ext>py[co]?$)', re.IGNORECASE)
logging = logging.getLogger('coremod')
from simpbot import localedata

i18n = localedata.get()


class coremod(control.control):
    def __init__(self, path=mods_path):
        self.core = coremodules
        self.path = path
        super(coremod, self).__init__('global.simpbot.modules')

    def __iter__(self):
        return iter(list(self.core.items()))

    def find_module(self, mod_name):
        return imp.find_module(mod_name, self.path)

    def load_module(self, modname, addmod=True, return_mod=True, trace=False):
        data = self.find_module(modname)
        #logging.debug(i18n['trying load'], modname)
        try:
            mod = imp.load_module(modname, *data)
        except Exception as error:
            logging.error(i18n['module with errors'], modname, error)
            if trace:
                for line in traceback.format_exc().splitlines():
                    logging.error('Exception: %s: %s' % (modname, line))
            return error
        else:
            logging.info(i18n['module loaded'], modname)
        if addmod:
            simmod = self.get_module(modname)
            simmod.load_meta(mod)
        if return_mod:
            return mod

    def download_module(self, modname):
        if modname in self.core:
            self.core[modname].reset()
            del self.core[modname]
            return True
        else:
            return False

    def reload_module(self, modname):
        if modname in self.core:
            mod = self.core[modname]
            if mod.rechargable():
                mod.reload()
                return True
        return False

    def get_module(self, modname=None, sys=False):
        if modname is None:
            modname = sys_._getframe(1).f_globals['__name__']
        if modname in self.core:
            return self.core[modname]
        else:
            mod = module.module(modname)
            if sys:
                if modname in sys_.modules:
                    mod.load_meta(sys_.modules[modname])
            self.core[modname] = mod
            return mod

    def del_module(self, modname):
        if modname in self.core:
            mod = self.core[modname]
            if mod.__class__ is module.module:
                if len(mod) > 0:
                    mod.reset()
            del self.core[modname]
            del mod
            return True
        else:
            return False

    def has_module(self, modname):
        return modname in self.core