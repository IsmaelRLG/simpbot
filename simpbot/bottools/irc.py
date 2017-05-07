# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import re, string
from . import text
from simpbot.envvars import networks

_alphanum = frozenset(string.ascii_letters + string.digits)
mask_regex = re.compile('(.+)!(.+)@(.+)')


def escape(pattern, no_parse=''):
    "Escape all non-alphanumeric characters in pattern."
    s = list(pattern)
    alphanum = _alphanum
    for i, c in enumerate(pattern):
        if c not in alphanum and c not in no_parse:
            if c == "\000":
                s[i] = "\\000"
            else:
                s[i] = "\\" + c
    return pattern[:0].join(s)


def parse_mask(mask):
    text.randphras()
    if '*' in mask:
        rand = '*'
        mask = escape(mask, '*!@')
        _mask = mask_regex.match(mask)
        if _mask is None:
            return mask
        res = []

        for gr in _mask.group(1, 2, 3):
            if gr.count(rand) == 0:
                pass
            else:
                if gr.startswith(rand):
                    if gr.count(rand) == 1:
                        gr = gr.replace(rand, '(.+)', 1)
                    else:
                        gr = gr.replace(rand, '(.+)?', 1)
                if gr.endswith(rand):
                    gr = gr[::-1].replace(rand[::-1], '(.+)?'[::-1], 1)[::-1]

                if gr.count(rand) > 0:
                    gr = gr.replace(rand, '(.+)')
            res.append(gr)

        return '%s!%s@%s' % tuple(res)
    return mask


def valid_mask(mask):
    return mask_regex.match(mask) is not None


def ischannel(channel, network=None, irc=None):
    chantypes = '#'  # Default
    if network and network in networks:
        irc = networks[network]

    if hasattr(irc.features, 'chantypes'):
        chantypes = irc.features.chantypes

    for l in chantypes:
        if channel.startswith(l):
            return True
    else:
        return False


colors = {
    'b': '\2',  # Bold
    "00": '\00300',  #
    "01": '\00301',  #
    "02": '\00302',  #
    "03": '\00303',  #
    "04": '\00304',  #
    "05": '\00305',  #
    "06": '\00306',  #
    "07": '\00307',  #
    "08": '\00308',  #
    "09": '\00309',  #
    "10": '\00310',  #
    "11": '\00311',  #
    "12": '\00312',  #
    "13": '\00313',  #
    "14": '\00314',  #
    "15": '\00315',  #
    }


def color(text, color__, bgcolor=None, bold=False):
    if isinstance(color__, int):
        color__ = str(color__).zfill(2)
    if len(color__) > 1 and color__.startswith('b'):
        color__ = color__.replace('b', '').zfill(2)
        text = color(text, 'b')
    if bgcolor is None:
        bgcolor = ''
    elif isinstance(bgcolor, int):
        bgcolor = str(bgcolor).zfill(2)
    if bold is True:
        text = color(text, 'b')
    color__ = colors[color__] if color__ in colors else ''
    bgcolor = colors[bgcolor].replace('\3', '') if bgcolor in colors else ''
    if not text.startswith(color__):
        text = color__ + (',' + bgcolor if bgcolor != '' else bgcolor) + text
    if color__.startswith('\3') and not text.endswith('\3'):
        text += '\3'
    if color__.startswith('\2') and not text.endswith('\2'):
        text += '\2'
    return text
