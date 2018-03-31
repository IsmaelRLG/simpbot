# coding=utf8
"""
database/cache.py - cache in memory for database.py --EDIT THIS--

Copyright © 2016-2018, Ismael Lugo, <ismaelrlgv@gmail.com>
Licensed under the MIT License.
"""
from __future__ import absolute_import, unicode_literals

import re
import time
import uuid
import hashlib
from six import string_types

from simpbot import schedule
from simpbot.envvars import CacheIns
from simpbot.settings import NO_EXISTS, NO_M_LINK, NO_M_KEY

scheduler = schedule.getroot()


class BaseCache(object):
    TYPE = {'int': int, 'str': str, 'float': float, 'bool': bool}

    @classmethod
    def extract(cls, obj, extr, name, type):
        if extr == 'all':
            v = obj
        elif extr == 'attr':
            v = getattr(obj, name)
        elif extr == 'key':
            v = obj[name]
        elif extr == 'index':
            v = None
            for index in map(int, name.split(':')):
                if v is None:
                    v = obj[index]
                else:
                    v = v[index]
        if type:
            v = cls.TYPE[type](v)
        return v

    @classmethod
    def rule(cls, rule_text):
        r = cls.RE_PARSE.match(rule_text)
        if r is None:
            raise ValueError("Invalid rule: %s" % rule_text)
        r = r.groupdict()
        if ':' in r['extract']:
            r['extract'] = r['extract'].split(':', 1)[0]
        r['extract'] = r['extract'].lower()
        if r['type']:
            r['type'] = r['type'].lower()
        return r


class Cache(BaseCache):

    def __init__(self, up_to_date=True, check=s.UP_TO_DATE_CACHE):
        self.args_map = {}
        self.link_map = {}
        self.reverse_map = {}
        self.schedule = up_to_date
        self.__up = False
        if up_to_date:
            scheduler.new_job(self.up_to_date, check)

    def cache(self, meta):
        assert 'store' in meta
        assert 'store' in meta['store']
        map = meta.get('mapper', mapper)
        uniq = meta.get('uniq')
        m_link = meta.get('link', NO_M_LINK)
        if m_link != NO_M_LINK:
            m_link = map(m_link, uniq)

        if 'key' in meta['store']:
            m_key = map(meta['store']['key'], uniq)
        else:
            m_key = NO_M_KEY

        if m_key == NO_M_KEY or m_link == NO_M_LINK:
            u_key = uuid.uuid4().hex
        else:
            u_key = None

        m_store = self.rule(meta['store']['store'])
        skip = meta['store']['skip'] if 'skip' in meta['store'] else ()
        duration = meta['duration'] if 'duration' in meta else None

        if not self.schedule and duration is not None:
            raise ValueError('"duration" not supported')

        def funcwrap(function):
            def argwrap(*args, **kwargs):
                if u_key is None:
                    link = m_link.generate(args, kwargs)
                else:
                    link = u_key

                search = self.search_link(link)
                if search == NO_EXISTS:
                    result = function(*args, **kwargs)
                    if u_key is None:
                        key = m_key.generate(args, kwargs, result)
                    else:
                        key = u_key
                    store = self.extract(m_store, result)
                    if store in skip:
                        return store

                    self.add_object(key, store, duration)
                    if key not in self.reverse_map:
                        self.reverse_map[key] = []
                    if link not in self.link_map:
                        self.link_map[link] = key
                    if link not in self.reverse_map:
                        self.reverse_map[key].append(link)
                    return result
                else:
                    return search

            if 'class' in meta and meta['class'] is True:
                def class_argwrap(*args, **kwargs):
                    return argwrap(*args[1:], **kwargs)
                return class_argwrap
            else:
                return argwrap
        funcwrap.u_key = u_key
        funcwrap.m_key = m_key
        funcwrap.m_link = m_link

        funcwrap.meta = meta
        return funcwrap

    def search_link(self, link):
        if link not in self.link_map:
            return NO_EXISTS

        key = self.link_map[link]
        if key not in self.args_map:
            # Dead link
            self.del_object(key)
            return NO_EXISTS

        value = self.args_map[key]
        if 'DURATION' in value:
            print('Alive: %s' % (time.time() - value['DATE']))
            if (time.time() - value['DATE']) >= value['DURATION']:
                self.del_object(key)
                return NO_EXISTS
        return value['OBJECT']

    def search_args(self, *args, **kwargs):
        return self.search_link(self.gen_link(*args, **kwargs))

    def add_object(self, key, object, duration=None):
        if key in self.args_map:
            raise KeyError('Key already exists: %s' % key)
        value = {'OBJECT': object}
        if duration is not None:
            value['DATE'] = time.time()
            value['DURATION'] = duration
        self.args_map[key] = value

    def del_object(self, key):
        if key in self.args_map:
            del self.args_map[key]

        if key in self.reverse_map:
            for link in self.reverse_map[key]:
                if link in self.link_map:
                    del self.link_map[link]
            del self.reverse_map[key][:]
            del self.reverse_map[key]

    def up_to_date(self):
        epoch = time.time()
        self.__up = True
        for key in list(self.args_map.keys()):
            val = self.args_map[key]
            if 'DURATION' in val:
                if (epoch - val['DATE']) < val['DURATION']:
                    continue
                # else DATE >= DURATION
                self.del_object(key)

    def clear(self):
        while self.__up:
            time.sleep(0.06)
        self.reverse_map.clear()
        self.args_map.clear()


class mapper(BaseCache):
    RE_PARSE = '((?P<type>int|str|float|bool):)?'
    RE_PARSE += '((?P<extract>(attr|key|index):(?P<name>[^ ]+)|all))'
    RE_PARSE = re.compile(RE_PARSE, re.IGNORECASE)

    @classmethod
    def hash(cls, text):
        return hashlib.md5(text).hexdigest()

    @classmethod
    def id(cls, args, kwargs, extra=None, uniq=None):
        lineal = map(repr, args) + map(repr, kwargs.values())
        lineal.sort()
        text = '|'.join([
            ';'.join(lineal),
            extra if extra else '',
            uniq if uniq else ''])
        return cls.hash(text)

    @classmethod
    def argsmap(cls, **kwargs):
        index = []
        for i in kwargs.values():
            if isinstance(i, (tuple, list)):
                index.append((i[0], cls.rule(i[1])))
            elif isinstance(i, string_types):
                continue
            else:
                index.append(i)
        index.sort()
        index = tuple(index)
        keys = []
        result = {}
        for key, value in kwargs.items():
            if isinstance(value, (tuple, list)):
                keys.append((key, cls.rule(value[1])))
            elif key == '__result':
                result.update(cls.rule(value))
            else:
                keys.append(key)
        if len(result) == 0:
            result = None
        keys.sort()
        keys = tuple(keys)
        return (index, keys, result)

    @classmethod
    def parse(cls, argls, rules_ls, type):
        dest = type()
        for rule in rules_ls:
            try:
                if isinstance(rule, (tuple, list)):
                    pos, rule = rule
                    dest.append(repr(cls.extract(argls[pos], **rule)))
                else:
                    dest.append(repr(argls[rule]))
            except (IndexError, KeyError):
                continue
        return dest

    def __init__(self, argsmap, uniq=False):
        self.index, self.keys, self.result = argsmap
        if isinstance(uniq, string_types):
            self.uniq = uniq
        elif uniq is True:
            self.uniq = uuid.uuid4().hex
        else:
            self.uniq = None

    def generate(self, args, kwargs, result=None):
        _args = self.parse(args, self.index, list)
        _kwargs = self.parse(kwargs, self.keys, dict)
        _result = None
        if result and self.result:
            _result = self.extract(result, **self.result)
        return self.id(_args, _kwargs, _result, self.uniq)


def getCache(name, **kwargs):
    if name in CacheIns:
        return CacheIns[name]
    CacheIns[name] = Cache(**kwargs)
    return CacheIns[name]
