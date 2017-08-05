# -*- coding: utf-8 -*-
# IRC (Internet Relay Chat) protocol client library for Python
# Maintainer:
#    Jason R. Coombs <jaraco@jaraco.com>
# Original Author:
#    Joel Rosdahl <joel@rosdahl.net>

# Copyright © 1999-2002 Joel Rosdahl
# Copyright © 2011-2015 Jason R. Coombs
# Copyright © 2009 Ferry Boender

from __future__ import unicode_literals, absolute_import

import re
import logging


log = logging.getLogger('simpbot')


class LineBuffer(object):

    line_sep_exp = re.compile(b'\r?\n')

    def __init__(self):
        self.buffer = b''

    def feed(self, bytes):
        self.buffer += bytes

    def lines(self):
        lines = self.line_sep_exp.split(self.buffer)
        # save the last, unfinished, possibly empty line
        self.buffer = lines.pop()
        return iter(lines)

    def __iter__(self):
        return self.lines()

    def __len__(self):
        return len(self.buffer)
