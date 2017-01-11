# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2017, Ismael Lugo (kwargs)

import re
import sys
from os import path
from . import workarea

logging = __import__('logging').getLogger('localedata')


class Error(Exception):
    def __init__(self, string, line=None, extra=None):
        if line is not None:
            string = string + ' in line #%s' % line
        if extra is not None:
            string = string + ': ' + extra
        self.string = string

    def __str__(self):
        return self.string


class MsgidError(Error):
    def __init__(self, string, msgid=None, line=None, extra=None, package=None):
        if package is not None:
            string += ' Package: "%s"' % package
        if msgid is None:
            string = 'msgid ' + string
        else:
            string = 'msgid "' + msgid + '"" ' + string
        super(MsgidError, self).__init__(string, line, extra)


class MsgstrError(Error):
    pass


class ConfigError(Error):
    pass


class LocaleData:

    def __init__(self, abspath, comment_prefixes=('#',)):
        self.localedata = workarea.workarea(abspath)
        self.comment_prefixes = comment_prefixes
        self.optregex = re.compile('(?P<option>msgid|msgstr|msgend|config) {0,}'
        '(?P<value>.*)?', re.IGNORECASE)
        self.cache = {}

    def exists(self, lang, package):
        """
        Check whether locale data is available for the given locale.  Ther
        return value is `True` if it exists, `False` otherwise.

        :param lang: language code
        :param package: the package name
        """
        return self.localedata.exists('%s:%s.dat' % (lang.upper(), package))

    def langs(self, package):
        """Return a list of all languages availables for a package.

        :param package: the package name
        """
        package = '%s.dat' % package
        avail = []
        for locale in self.localedata.listdir():
            try:
                lang, pack = locale.split(':')
            except ValueError:
                raise Error('Invalid locale name: %s', locale)
            if pack == package:
                avail.append(lang.upper())
        return avail

    def in_cache(self, lang, package_name):
        return lang in self.cache and package_name in self.cache[lang]

    def _read(self, fp, lang, package_name, abspath, update_cache=False):
        lang = lang.upper()
        if self.in_cache(lang, package_name) and not update_cache:
            return

        read = fp.read()

        strip = True
        tostrip = ''
        addline = False
        comment = True
        nline = 0
        equal = lambda bool: bool == 'yes'

        def chkequal(bool, line):
            if not bool in ('yes', 'y', 'not', 'no', 'n'):
                raise ConfigError('Bad boolean', nline, line)

        def stripequal(value):
            value = value.strip()
            chkequal(value, line)
            return equal(value)

        last_msgid = None
        msgid_line = None
        localedata = Locale(lang, package_name, abspath)

        for line in read.splitlines():
            nline += 1
            if line == '' and not addline:
                continue

            if strip and not line.isspace() and line.startswith(' '):
                if tostrip:
                    line = line.replace(strip, 1)
                else:
                    line = line.lstrip()

            # comment line?
            comment_line = False
            for prefix in self.comment_prefixes:
                if line.startswith(prefix) and comment:
                    comment_line = True
                    break
            if comment_line:
                continue

            res = self.optregex.match(line)
            if res:
                opt, value = res.group('option', 'value')
                if opt == 'config' and value:
                    try:
                        config, value = value.lower().split(' ', 1)
                    except ValueError:
                        raise ConfigError('Bad config', nline, line)

                    if config == 'nostrip':
                        strip = stripequal(value)
                        continue
                    elif config == 'addline':
                        addline = stripequal(value)
                        continue
                    elif config == 'comment':
                        comment = stripequal(value)
                        continue
                    else:
                        raise ConfigError('Bad boolean', nline, line)

                elif opt == 'msgid':
                    if value is None or value == '':
                        raise MsgidError('missing value', None, nline, line, package_name)
                    elif not last_msgid is None and localedata[last_msgid] is None:
                        raise MsgidError('without msgstr', last_msgid, msgid_line, package_name)

                    localedata[value] = None
                    last_msgid = value
                    msgid_line = nline
                    strip = True
                    tostrip = ''
                    addline = False
                elif opt == 'msgstr':
                    if value is None:
                        value = ''
                    if last_msgid is None:
                        raise MsgstrError('msgstr without msgid', nline)

                    if localedata[last_msgid] is None:
                        if value != '' and addline:
                            value += '\n'
                        localedata[last_msgid] = value
                        continue
                    if addline:
                        value += '\n'
                    localedata[last_msgid] += value
                elif opt == 'msgend':
                    if not last_msgid is None:
                        continue
                    elif localedata[last_msgid] is None:
                        raise MsgidError('without msgstr', last_msgid, msgid_line, package_name)

                    last_msgid = None
                    strip = True
                    tostrip = ''
                    addline = False

            else:
                if not last_msgid is None:
                    continue
                localedata[last_msgid] += line
        if not lang in self.cache:
            self.cache[lang] = {}
        self.cache[lang][package_name] = localedata

    def read(self, lang, package):
        if not self.exists(lang, package):
            return 0
        lang = lang.upper()
        abspath = self.localedata.join('%s:%s.dat' % (lang, package))
        with open(abspath, 'r') as fp:
            self._read(fp, lang, package, abspath)
        return 1

    def get(self, lang, package):
        lang = lang.upper()
        if self.in_cache(lang, package):
            return self.cache[lang][package]

    def clear_cache(self):
        self.cache.clear()

    def remove_from_cache(self, lang, package):
        lang = lang.upper()
        if self.in_cache(lang, package):
            del self.cache[lang][package]
            return 1
        return 0


class Locale:

    def __init__(self, lang, package_name, abspath):
        self.lang = lang
        self.msgid = {}
        self.package = package_name
        self.abspath = abspath

    def __call__(self, msgid):
        return self.__getitem__(msgid)

    def __repr__(self):
        return "<locale lang='%s' path='%s'>" % (self.lang, self.abspath)

    def __getitem__(self, msgid):
        if msgid in self.msgid:
            return self.msgid[msgid]
        else:
            raise MsgidError('Invalid MSGID: ' + msgid)

    def __delitem__(self, msgid):
        if msgid in self.msgid:
            del self.msgid[msgid]
        else:
            raise MsgidError('Invalid MSGID: ' + msgid)

    def __setitem__(self, msgid, msgstr):
        if msgid in self.msgid and self.msgid[msgid] is not None:
            logging.warning("Package: '%s' MSGID: '%s' updating MSGTR!",
            self.abspath, msgid)
        self.msgid[msgid] = msgstr

    def msgid(self, msgid, msgstr=None):
        if msgstr is not None:
            self.__setitem__(msgid, msgstr)
        else:
            return self.__getitem__(msgid)

    def remove(self, msgid):
        self.__delitem__(msgid)

    def has_msgid(self, msgid):
        return msgid in self.msgid


simplocales = LocaleData(path.join(path.dirname(__file__), 'localedata'))


def get(lang=None, package=None):
    from . import envvars
    if package is None:
        package = sys._getframe(1).f_globals['__name__']
    if lang is None:
        lang = envvars.default_lang

    if simplocales.exists(lang, package):
        if not simplocales.in_cache(lang, package):
            simplocales.read(lang, package)
        return simplocales.get(lang, package)

    langs = simplocales.langs(package)
    if len(langs) == 0:
        raise Error('Invalid package ' + package)
    elif len(langs) == 1:
        if not simplocales.in_cache(lang, package):
            simplocales.read(lang, package)
        return simplocales.get(langs[0], package)
    elif 'EN' in langs:
        if not simplocales.in_cache('EN', package):
            simplocales.read('EN', package)
        return simplocales.get('EN', package)
    else:
        raise Error('Invalid lang for %s, only support %s' % (package, lang))