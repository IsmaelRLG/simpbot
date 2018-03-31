# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import re
import types
import logging
from simpbot import control
from simpbot import parser
from six.moves._thread import start_new
from six import string_types
logging = logging.getLogger('CommandHandler')
from simpbot import localedata

_locale = localedata.get()

record_formats = {
    ':user-info:': '{user.mask} ({user.account})',
    ':date-info:': '(%F)[%X]',
    ':netw-name:': '{irc.servname}',
    ':admin-info:': '{user.admin.user}',
    ':base-info:': '',
    ':admins:': ':date-info: :user-info: :netw-name: :admin-info:: {message}',
    ':simple:': ':date-info: :user-info: :netw-name:: {message}'}


def get_format(string):
    for name in record_formats:
        if name in string:
            string = string.replace(name, record_formats[name])
            for _name in record_formats:
                if _name in string:
                    string = string.replace(_name, get_format(_name))
            continue
    return string


class handler(control.control):

    def __init__(self, func, name, regex, helpmsg, syntax, alias, need,
        module=None, strip=None, i18n=None, record=None):
        self.func = func

        if isinstance(i18n, dict) and not 'loader' in i18n:
            raise ValueError('missing locale loader')
        self.i18n = i18n
        self.name = name
        self.alias = alias
        self.module = module
        self.syntax = syntax
        self.need = need

        if isinstance(record, string_types):
            self.rec_form = get_format(record)
        else:
            self.rec_form = record

        if self.name is None:
            self.name = func.__name__
        self.name = self.name.strip()
        self.helpmsg = helpmsg
        if self.helpmsg is None:
            if isinstance(func, types.FunctionType):
                self.helpmsg = func.__doc__

        if strip and self.helpmsg:
            self.helpmsg = self.strip(self.helpmsg, strip)

        if regex is None or len(regex) == 0:
            self.regex = None
        elif isinstance(regex, dict):
            self.regex = {}
            for k, expr in regex.items():
                self.regex[k] = re.compile(parser.ParserRegex(expr).string, 2)
        else:
            self.regex = parser.ParserRegex(regex).string
            self.regex = re.compile(self.regex, re.IGNORECASE)
            self.match = self.regex.match
            self.findall = self.regex.findall
            self.scanner = self.regex.scanner
            self.search = self.regex.search
        if isinstance(i18n, dict) and 'module' in i18n:
            self.mod_name = i18n['module']
        elif self.module is None:
            self.mod_name = 'unbound-module'
        else:
            self.mod_name = self.module.name
        super(handler, self).__init__('%s.%s' % (self.mod_name, self.name))

    def __call__(self, *args):
        start_new(self.function, args, {})

    def execute(self, *args, **kwargs):
        # Non thread
        self.func(*args, **kwargs)

    def has_helpmsg(self):
        if not self.i18n and not self.helpmsg:
            return False
        return 'help' in self.i18n or 'helpmsg' in self.i18n or self.helpmsg

    def has_syntax(self):
        return self.i18n and 'syntax' in self.i18n or self.syntax is not None

    def has_alias(self):
        return self.i18n and 'alias' in self.i18n or self.alias is not None

    def function(self, irc, event, result, target, channel, _, locale):
        try:
            self.func(irc, event, result, target, channel, _, locale)
        except SystemExit as err:
            _['handler'] = self
            _['message'] = repr(err)
            irc.verbose('error', _(_locale['exception info']))
            logging.error(_(_locale['exception info']))

    @staticmethod
    def strip(text, strip):
        newtext = []
        for line in text:
            if line.startswith(strip):
                line = line.replace(strip, '', 1)
            elif line == '' and len(newtext) == 0:
                continue
            newtext.append(line)
        return '\n'.join(newtext)

    def get_help(self, lang, meta):
        if self.i18n and self.mod_name:

            if meta in self.i18n:
                return localedata.get(lang, self.mod_name)[self.i18n[meta]]

        if meta == 'help' or meta == 'helpmsg':
            return self.helpmsg
        elif meta == 'syntax':
            return self.syntax
        elif meta == 'alias':
            return self.alias
        else:
            raise ValueError('Invalid metavalue: ' + meta)