# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)


class ReadConf:
    def __init__(self, abspath, comment_prefix=('#',)):
        self.abspath = abspath
        self.comment_prefix = comment_prefix
        self.data = {}
        if not self.abspath is None:
            self.read()

    def __getitem__(self, opt):
        return self.data[opt]

    def __setitem__(self, opt, value):
        self.data[opt] = value

    def __detitem__(self, opt):
        del self.data[opt]

    def __iter__(self):
        return iter(self.data)

    def _read(self, fp):
        n_line = 0
        for line in fp.read().splitlines():
            n_line += 1
            line = line.lstrip()
            if line == '' or line[0] in self.comment_prefix or not '=' in line:
                continue

            try:
                opt, val = line.split('=', 1)
            except ValueError:
                continue

            opt, val = opt.strip(), val.lstrip()
            if opt == '' or opt in self.data:
                raise ValueError('Invalid conf, line #%s' % n_line)

            self.data[opt] = val

    def get(self, opt, default=None):
        try:
            data = self.__getitem__(opt)
            if data == '' and default:
                return default
            else:
                return data
        except KeyError:
            if default:
                return default
            else:
                errormsg = '%s: Option not found "%s"' % (self.abspath, opt)
                raise KeyError(errormsg)

    def read(self):
        with open(self.abspath, 'r') as fp:
            self._read(fp)

    def getboolean(self, opt):
        val = self.__getitem__(opt).strip().lower()
        if not val in ('yes', 'not', 'no'):
            raise ValueError
        return val == 'yes'

    def getint(self, opt, default=None):
        return int(self.get(opt, default))

    def _save(self, fp):
        for opt, value in self.data.values():
            fp.write('%s = %s' % (opt, value))

    def save(self):
        with open(self.abspath, 'w') as fp:
            self._save(fp)