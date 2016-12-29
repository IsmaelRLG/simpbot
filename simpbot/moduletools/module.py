# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import logging
from simpbot import control
from types import ModuleType
from handler import handler as handlermsg
logging = logging.getLogger('module')


class module(control.control):

    def __init__(self, mod, version=None, author=None):
        self.handlers = {}

        if isinstance(mod, ModuleType):
            self.module = mod
            self.load_meta()
        elif isinstance(mod, basestring):
            self.module = None
            self.name = mod
            self.version = version
            self.author = author
        super(module, self).__init__(self.name)

    def __repr__(self):
        text = '<SimpBot-module "%s"%s>'
        text = text % (self.name, ', v' + self.version if self.version else '')
        return repr(text)

    def __len__(self):
        return len(self.handlers)

    def __iter__(self):
        return iter(self.handlers)

    def setattr(self, obj, attr, name, default=None):
        if hasattr(obj, attr):
            setattr(self, name, getattr(obj, attr))
        else:
            self.version = default

    def rechargable(self):
        return isinstance(self.module, ModuleType)

    @staticmethod
    def ishandler(handler):
        return isinstance(handler, handlermsg)

    def load_meta(self, module=None):
        if not module is None:
            self.module = module
        self.setattr(self.module, '__name__', 'name')
        self.setattr(self.module, '__version__', 'version')
        self.setattr(self.module, '__author__', 'author')
        self.setattr(self.module, '__file__', 'abspath')
        self.setattr(self.module, '__package__', 'package')

    def add_handler(self, handler):
        if self.ishandler(handler):
            if not handler.name in self.handlers:
                self.handlers[handler.name] = handler

    def del_handler(self, handler):
        if self.ishandler(handler):
            name = handler.name
        else:
            name = handler
        del self.handlers[name]

    def has_handler(self, handler):
        if self.ishandler(handler):
            name = handler.name
        else:
            name = handler
        return name in self.handlers

    def get_handler(self, handler):
        if self.ishandler(handler):
            name = handler.name
        else:
            name = handler
        return self.handlers[name]

    def reset(self):
        self.handlers.clear()

    def reload(self):
        self.reset()
        if isinstance(self.module, ModuleType):
            reload(self.module)
            self.load_meta()

    def handlers_names(self):
        return self.handlers.keys()

    def loader(self):
        def mod_loader(name=None, regex=None, help=None, syntax=None,
            alias=None, need=[], strip=None):
            def handler(func):
                handler = handlermsg(func, name, regex, help, syntax, alias,
                need, self, strip)
                self.add_handler(handler)

                return handler
            return handler
        return mod_loader
