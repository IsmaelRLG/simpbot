# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

from __future__ import absolute_import
from six import string_types


def parse_targets(mode, targets, p=4, nmode=False):
    if isinstance(targets, string_types):
        targets = targets.split()
    targets = list(targets)
    if not nmode:
        if len(mode) <= 1:
            return
        else:
            mm = mode[0]
            mode = mode[1]
    parse = []
    rounds = float(len(targets)) / p
    if not rounds.is_integer():
        rounds += 1
    rounds = int(rounds)
    targets.reverse()
    for i in range(rounds):
        t = []
        for n in range(p):
            try:
                t.append(targets.pop())
            except IndexError:
                break
        if nmode:
            parse.append(' '.join(t))
        else:
            parse.append('{0}{1} {2}'.format(mm, len(t) * mode, ' '.join(t)))
    return parse


# IRC (Internet Relay Chat) protocol client library for Python
# Maintainer:
#    Jason R. Coombs <jaraco@jaraco.com>
# Original Author:
#    Joel Rosdahl <joel@rosdahl.net>

# Copyright © 1999-2002 Joel Rosdahl
# Copyright © 2011-2015 Jason R. Coombs
# Copyright © 2009 Ferry Boender


def parse_nick_modes(mode_string):
    """Parse a nick mode string.

    The function returns a list of lists with three members: sign,
    mode and argument.  The sign is "+" or "-".  The argument is
    always None.

    Example:

    >>> parse_nick_modes("+ab-c")
    [['+', 'a', None], ['+', 'b', None], ['-', 'c', None]]
    """

    return _parse_modes(mode_string, "")


def parse_channel_modes(mode_string):
    """Parse a channel mode string.

    The function returns a list of lists with three members: sign,
    mode and argument.  The sign is "+" or "-".  The argument is
    None if mode isn't one of "b", "k", "l", "v", "o", "h", or "q".

    Example:

    >>> parse_channel_modes("+ab-c foo")
    [['+', 'a', None], ['+', 'b', 'foo'], ['-', 'c', None]]
    """
    return _parse_modes(mode_string, "bklvohq")


def _parse_modes(mode_string, unary_modes="", only=""):
    """
    Parse the mode_string and return a list of triples.

    If no string is supplied return an empty list.
    >>> _parse_modes('')
    []

    If no sign is supplied, return an empty list.
    >>> _parse_modes('ab')
    []

    Discard unused args.
    >>> _parse_modes('+a foo bar baz')
    [['+', 'a', None]]

    Return none for unary args when not provided
    >>> _parse_modes('+abc foo', unary_modes='abc')
    [['+', 'a', 'foo'], ['+', 'b', None], ['+', 'c', None]]

    This function never throws an error:
    >>> import random
    >>> import six
    >>> unichr = chr if six.PY3 else unichr
    >>> def random_text(min_len = 3, max_len = 80):
    ...     len = random.randint(min_len, max_len)
    ...     chars_to_choose = [unichr(x) for x in range(0,1024)]
    ...     chars = (random.choice(chars_to_choose) for x in range(len))
    ...     return ''.join(chars)
    >>> def random_texts(min_len = 3, max_len = 80):
    ...     while True:
    ...         yield random_text(min_len, max_len)
    >>> import itertools
    >>> texts = itertools.islice(random_texts(), 1000)
    >>> set(type(_parse_modes(text)) for text in texts) == set([list])
    True
    """

    # mode_string must be non-empty and begin with a sign
    if not mode_string or not mode_string[0] in '+-':
        return []

    modes = []

    parts = mode_string.split()

    mode_part, args = parts[0], parts[1:]

    for ch in mode_part:
        if ch in "+-":
            sign = ch
            continue
        if only and not ch in only:
            continue
        arg = args.pop(0) if ch in unary_modes and args else None
        modes.append([sign, ch, arg])
    return modes



