# -*- coding: utf-8 -*-

import os
import sys
import re
#from .core import refile

abspath = os.path.dirname(__file__)
ext_allow = ['.py']
refile = re.compile('(?P<name>.+)\.(?P<ext>py[co]?$)', re.IGNORECASE)
PYDIR = 1
PYEXE = 2
PYCMP = 3


class modloader:

    def __init__(self, module, path=None, ext_allow=['py']):
        if path is None:
            _vars = self.get_vars()
            if not '__file__' in _vars:
                raise ValueError('Argument "path" is required')
            path = os.path.dirname(_vars['__file__'])
            if path == '':
                path = os.getcwd()
        self.module = module
        self.abspath = path
        self.ext_allow = ext_allow

    @staticmethod
    def get_vars():
        try:
            raise Exception
        except:
            return sys.exc_info()[2].tb_frame.f_globals

    def mod_list(self):
        mods = {}

        for dirpath, dirnames, filenames in os.walk(self.abspath):
            # processing dirs...
            for _dir in dirnames:
                if os.path.exists(os.path.join(dirpath, _dir, '__init__.py')):
                    mods[_dir] = (os.path.join(dirpath, _dir), PYDIR)

            # processing files...
            for _file in filenames:
                matchres = refile.match(_file)
                if matchres is None:
                    continue
                elif matchres.group('ext').lower() in self.ext_allow:
                    if matchres.group('name') != '__init__':
                        mods[matchres.group('name')] = \
                        (os.path.join(dirpath, _file), PYEXE)
            break
        return mods.items()
