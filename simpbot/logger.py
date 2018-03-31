# coding=utf8
"""
logger.py - unification and formatting of records.

Copyright © 2016-2018, Ismael Lugo, <ismaelrlgv@gmail.com>
Licensed under the MIT License.
"""

from __future__ import absolute_import, unicode_literals

import os
import time
import codecs
import logging
from logging.handlers import TimedRotatingFileHandler as TRFH
from simpbot import settings as s
from simpbot import envvars as e


class StrftimeRotating(TRFH):
    def __init__(self, outdir, format):
        self.outdir = outdir
        self.format = format
        super(StrftimeRotating, self).__init__(self.filename, when='midnight')

    @property
    def filename(self):
        return os.path.join(self.outdir, time.strftime(self.format))

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        self.baseFilename = self.filename
        if self.encoding:
            self.stream = codecs.open(self.baseFilename, 'w', self.encoding)
        else:
            self.stream = open(self.baseFilename, 'w')
            self.rolloverAt = self.rolloverAt + self.interval


def getIRCLogger(network, source):
    logger_name = 'client.%s.%s' % (network.lower(), source.lower())
    if logger_name in e.loggers:
        return e.loggers[logger_name][]
    logger = logging.getLogger('simpbot').getChild(logger_name)

    formatter = logging.Formatter(s.IRC_FORMAT, s.DATE_HOUR_FORMAT)
    if e.daemon:
        path = os.path.join(network.lower(), source.lower())
        e.log_irc.mkdir(path, parents=True)
        handler = StrftimeRotating(
            e.log_irc.join(path),
            '{}.log'.format(s.DATE_DAY_FORMAT))
    else:
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    e.loggers[logger_name] = logger
    return logger


def getLogger(name, level=s.DEFAULT_LEVEL, format=s.DEFAULT_FORMAT):
    if name in e.loggers:
        return e.loggers[name]
    logger = logging.getLogger(name)
    if e.daemon is True:
        formatter = logging.Formatter(e.FIL_FORMAT)
        handler = TRFH(e.log_abspath, when='midnight', backupCount=s.MAX_BACKUP)
    else:
        formatter = logging.Formatter(e.STD_FORMAT)
        handler = logging.StreamHandler()

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    e.loggers[name] = logger
    return logger
