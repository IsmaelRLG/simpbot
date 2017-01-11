# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import re
import types
import traceback
from simpbot import control
from simpbot import parser
from six.moves._thread import start_new
logging = __import__('logging').getLogger('CommandHandler')
from simpbot import localedata

i18n = localedata.get()


class handler(control.control):

    def __init__(self, func, name, regex, helpmsg, syntax, alias, need,
        module=None, strip=None):
        self.func = func
        self.name = name
        self.alias = alias
        self.module = module
        self.syntax = syntax

        self.need = need
        if self.name is None:
            self.name = func.__name__
        self.name = self.name.strip()
        self.helpmsg = helpmsg
        if self.helpmsg is None:
            if isinstance(func, types.FunctionType):
                self.helpmsg = func.__doc__

        if strip and self.helpmsg:
            newhelpmsg = []
            for line in self.helpmsg.splitlines():
                if line.startswith(strip):
                    line = line.replace(strip, '', 1)
                elif line == '' and len(newhelpmsg) == 0:
                    continue
                newhelpmsg.append(line)
            self.helpmsg = '\n'.join(newhelpmsg)

        if regex is None or len(regex) == 0:
            self.regex = None
        else:
            self.regex = parser.ParserRegex(regex).string
            self.regex = re.compile(self.regex, re.IGNORECASE)
            self.match = self.regex.match
            self.findall = self.regex.findall
            self.scanner = self.regex.scanner
            self.search = self.regex.search
        if self.module is None:
            self.mod_name = 'unbound-module'
        else:
            self.mod_name = self.module.name
        super(handler, self).__init__('%s.%s' % (self.mod_name, self.name))

    def __call__(self, irc, event, result, target, channel, _):
        start_new(self.function, (irc, event, result, target, channel, _), {})

    def execute(self, *args, **kwargs):
        # Non thread
        self.func(*args, **kwargs)

    def function(self, irc, event, result, target, channel, _):
        try:
            self.func(irc, event, result, target, channel, _)
        except:
            _['handler'] = self
            irc.verbose('error', _(i18n['error info']))
            for line in traceback.format_exc().splitlines():
                _['message'] = line
                irc.verbose('error', _(i18n['exception info']))
                logging.error(_(i18n['exception info']))
