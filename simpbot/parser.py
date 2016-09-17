# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import re
from time import strftime as date
from time import time as epoch
from datetime import timedelta


finder = re.compile("(!\{([^ !]+)\}(\d{0,})([sfbi])?([-+]{0,1}\??))").findall
###############
# TIPOS       #
###############
STRING = 's'
FLOAT = 'f'
BOOLEAN = 'b'
INT = 'i'


def parse_r(regex, *args):
    def regex_value(*values):
        if len(args) != len(values):
            return ''
        n = 0
        kw = {}
        for arg in args:
            kw[arg] = values[n]
            n += 1
        return regex.format(**kw)
    return regex_value


def parse_bool(boolean):
    if boolean is True:
        return 'sí'
    else:
        return 'no'

none_value = '?'


def is_none(string):
    if string is None:
        return none_value
    else:
        return string

parse_float = lambda f: float('%.2f' % f)
time = lambda date: timedelta(seconds=parse_float(epoch() - date))

#########################
# EXPRESIONES REGULARES #
#########################
uniq = parse_r('(?P<{name}>[^ ]+)', 'name')
uniq_opt = parse_r('({n_sep}(?P<{name}>[^ ]+))?', 'n_sep', 'name')
mult = parse_r('(?P<{name}>.+)', 'name')
mult_opt = parse_r('({n_sep}(?P<{name}>.+))?', 'n_sep', 'name')

value_arg = parse_r('(?P<{name}>{value})', 'name', 'value')
value_opt = parse_r('({n_sep}(?P<{name}>{value}))?', 'n_sep', 'name', 'value')


#########################
#  NOMBRES  RESERVADOS  #
#########################
renames = ['nickbot', 'nickname', 'network', 'channel', 'hostname', 'datetime']


class ParserRegex:

    def __init__(self, string):
        self.match = finder(string)
        self.string = string
        self.parse()

    def __str__(self):
        return self.string

    def __repr__(self):
        return repr('<%s (%s)>' % (self.__class__.__name__, hash(self.string)))

    def parse(self):
        for full, name, n_repl, type, end_point in self.match:
            if name in renames:
                continue

            if n_repl == '':
                n_sep = ' '
            else:
                n_sep = ' ' * int(n_repl)

            #if value != '':
                #if '?' in end_point:
                    #parse = value_opt(value, n_sep, name)
                #else:
                    #parse = value_arg(name)

            if end_point == '':
                parse = uniq(name)
            elif end_point == '?':
                parse = uniq_opt(n_sep, name)
            elif '-' in end_point:
                if '?' in end_point:
                    parse = uniq_opt(n_sep, name)
                else:
                    parse = uniq(name)
            elif '+' in end_point:
                if '?' in end_point:
                    parse = mult_opt(n_sep, name)
                else:
                    parse = mult(name)
            self.string = self.string.replace(full, parse)


class replace:
    def __init__(self, irc, result):
        self.mapping = {
            'network': irc.servname,
            'connected': parse_bool(irc.connected),
            'nickbot': irc.nickname
            }

        for group_name in result.re.groupindex.keys():
            self.mapping[group_name] = result.group(group_name)

    def __call__(self, string):
        return self.replace(string)

    def __getitem__(self, item):
        return self.mapping[item]

    def __setitem__(self, item, value):
        self.set(item, value)

    def __iter__(self):
        return iter(self.mapping)

    def set(self, item, value):
        self.mapping[item] = value

    def replace(self, string):
        return date(string.format(**self.mapping))