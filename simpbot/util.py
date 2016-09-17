# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import random
import logging
import os
import sys
from os import path
from re import match
from re import IGNORECASE
from imp import load_module
from time import strftime as date
from logging import basicConfig
from textwrap import wrap
from . import envvars
logging = logging.getLogger('TOOLS')


def debug(level):
    kw = {'level': level, 'format': '%(name)s - %(levelname)s: %(message)s'}
    if envvars.DAEMON is True:
        kw['filename'] = envvars.workarea.join('logs', date('%d%m%Y.log'))
        kw['filemode'] = 'a'
    basicConfig(**kw)


def loadmodule(filename):
    logging.debug('Intentando cargar: %s', filename)
    pydata = []
    sub = []
    if not path.exists(filename):
        logging.error('No existe el modulo %s', filename)
        return
    elif path.isfile(filename):
        r_match = match('(?P<name>.+)\.(?P<ext>py[co]?$)', filename, IGNORECASE)
        if r_match is None:
            logging.error('¿No es Python?: %s', filename)
            return
        if r_match.group('ext') in ('pyc', 'pyo'):
            return
        name = r_match.group('name')
        pydata.append(open(filename, 'U'))
        sub.extend(['.' + r_match.group('ext'), 'U', 1])
    elif path.isdir(filename):
        init = path.join(filename, '__init__.py')
        if not path.exists(init):
            logging.error('¿No es Python?: %s', filename)
            return
        elif path.isdir(init):
            logging.error('¿WTF? ¿Que hiciste? ¿Un directorio?: %s', filename)
            return
        else:
            name = filename
        pydata.append(None)
        sub.extend(['', '', 5])
    else:
        logging.warning('¿Enlace simbolico?: %s', filename)
        return

    pydata.append(filename)
    pydata.append(tuple(sub))
    return load_module(path.basename(name), *tuple(pydata))


def randphras(l=5, alpha=(True, True), num=True, noalpha=False, noinitnum=False):
    names = []
    if noalpha:
        n0 = '$ ¡ ! . + - [ ] { } ( ) ~ * % & / ¿ ? # " = ^ , < > | °'.split()
        names.append('n0')
    if alpha[0]:
        n1 = 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split()
        names.append('n1')
    if alpha[1]:
        n2 = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'.split()
        names.append('n2')
    if num:
        n3 = '1 2 3 4 5 6 7 8 9 0'.split()
        names.append('n3')
    phrass = ''
    for n in range(l):
        if len(phrass) == 0 and noinitnum:
            lyric = random.choice(n2)
        else:
            lyric = random.choice(eval(random.choice(names)))
        phrass += lyric
    return phrass


def textwrap(text):
    return wrap(text, 256, fix_sentence_endings=True, drop_whitespace=False)


def unicode_to_str(func):
    def wrapper(*args, **kwargs):
        new_args = []
        new_kwargs = {}

        # Argumentos Posicionales
        for arg in args:
            if isinstance(arg, unicode):
                new_args.append(arg.encode('utf-8'))
            else:
                new_args.append(arg)

        # Argumentos Clave
        for key, value in kwargs.items():
            if isinstance(value, unicode):
                new_kwargs[key] = value.encode('utf-8')
            else:
                new_kwargs[key] = value

        return func(*new_args, **new_kwargs)
    return wrapper


def deamonize(stdout, stderr, stdin, pidfile):
    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)   # Exit first parent.
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)

    os.chdir("/")
    os.umask(0)
    os.setsid()
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)   # Exit second parent.
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)
    si = file(stdin, 'r')
    so = file(stdout, 'a+')
    se = file(stderr, 'a+', 0)
    pid = str(os.getpid())
    if pidfile:
        file(pidfile, 'w+').write("%s\n" % pid)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())


def pid_exists(pid):
    import errno
    if pid < 0:
        return False
    if pid == 0:
        raise ValueError('invalid PID 0')
    try:
        os.kill(pid, 0)
    except OSError as err:
        if err.errno == errno.ESRCH:
            return False
        elif err.errno == errno.EPERM:
            return True
        else:
            raise
    else:
        return True

