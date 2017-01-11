# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import random
import string
from six import string_types
from six import text_type
from six import PY3 as python_3


def parse_args(instance, method, ignore_py3=False):
    def parser(func):
        if ignore_py3 and python_3:
            return func

        def wrapper(*args, **kwargs):
            new_args = []
            new_kwargs = {}
            # Argumentos Posicionales
            for arg in args:
                if isinstance(arg, instance):
                    new_args.append(method(arg))
                else:
                    new_args.append(arg)
            # Argumentos Clave
            for key, value in kwargs.items():
                if isinstance(value, instance):
                    new_kwargs[key] = method(value)
                else:
                    new_kwargs[key] = value
            return func(*new_args, **new_kwargs)
        return wrapper
    return parser

lower = parse_args(string_types, str.lower)
normalize = parse_args(text_type, lambda txt: txt.encode('utf-8'), True)


def part(string, parts, mark=''):
    if parts <= 0:
        return []
    elif len(string) <= parts:
        return [string]
    markl = len(mark)
    total_parts = float(len(string) + markl) / parts
    if not total_parts.is_integer():
        total_parts += 1
    total_parts = int(total_parts)
    part = 0
    init_point = 0
    splits = []
    while 1:
        part += 1
        if part == total_parts:
            splits.append(mark + string[init_point:])
            break
        elif init_point == 0:
            splits.append(string[:parts])
            init_point += parts
        else:
            splits.append(mark + string[init_point:(init_point + parts)])
            init_point += parts
    return splits


def randphras(l=5, upper=True, lower=True, digit=True, punct=False, nofd=False):
    names = []
    if punct:
        names.append('string.punctuation')
    if upper:
        names.append('string.ascii_uppercase')
    if lower:
        names.append('string.ascii_lowercase')
    if digit:
        names.append('string.digits')
    phrass = ''
    for n in range(l):
        if len(phrass) == 0 and nofd:
            char = random.choice(string.ascii_lowercase)
        else:
            char = random.choice(eval(random.choice(names)))
        phrass += char
    return phrass
