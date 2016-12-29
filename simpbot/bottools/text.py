# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import random


def parse_args(instance, met):
    def parser(func):
        def wrapper(*args, **kwargs):
            new_args = []
            new_kwargs = {}
            # Argumentos Posicionales
            for arg in args:
                if isinstance(arg, instance):
                    new_args.append(met(arg))
                else:
                    new_args.append(arg)
            # Argumentos Clave
            for key, value in kwargs.items():
                if isinstance(value, unicode):
                    new_kwargs[key] = met(value)
                else:
                    new_kwargs[key] = value
            return func(*new_args, **new_kwargs)
        return wrapper
    return parser


unicode_to_str = parse_args(unicode, str.encode)
lower = parse_args(basestring, str.lower)


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


def randphras(l=5, alpha=(True, True), num=True, noalpha=False, noinitnum=False):
    names = []
    if noalpha:
        n0 = part('$¡!.+_@¬-[]{}()~*%&/¿?#"=^,<>|\\·°\'% `', 1)  # lint:ok
        names.append('n0')
    if alpha[0]:
        n1 = part('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 1)  # lint:ok
        names.append('n1')
    if alpha[1]:
        n2 = part('abcdefghijklmnopqrstuvwxyz', 1)
        names.append('n2')
    if num:
        n3 = part('1234567890', 1)  # lint:ok
        names.append('n3')
    phrass = ''
    for n in range(l):
        if len(phrass) == 0 and noinitnum:
            lyric = random.choice(n2)
        else:
            lyric = random.choice(eval(random.choice(names)))
        phrass += lyric
    return phrass

