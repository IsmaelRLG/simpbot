# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import simpbot
import re

cc_manager = simpbot.envvars.data.new_wa('channel-control')
groups = ['clon', 'flood', 'link', 'repeat', 'upper', 'badwords']
conf_regex = '(?P<group_name>%s) (?P<netw>[^ ]+) (?P<chan>[^ ]+) (?P<cfg>[^ ]+)'
conf_regex = re.compile(conf_regex % groups)
conf_filename = 'channel_control.json'
wl_filename = '%s.wl'
wl_maker = lambda name: simpbot.control.control(wl_filename % name, cc_manager)

wl_clon,     clon     = wl_maker('clon'),     {}
wl_flood,    flood    = wl_maker('flood'),    {}
wl_link,     link     = wl_maker('link'),     {}
wl_repeat,   repeat   = wl_maker('repeat'),   {}
wl_upper,    upper    = wl_maker('upper'),    {}
wl_badwords, badwords = wl_maker('badwords'), {}
wl_generic,  generic  = wl_maker('generic'),  {}
main_conf = {}

def in_whitelist(inst, irc, user, channel, check_usr=True):
    if user.account is None:
        if not user.completed and check_usr:
            irc.request.request(user.nick)
            if not user.completed:
                try: irc.request.user(user.nick, timeout=irc.timeout)
                except ValueError: pass
            else:
                return in_whitelist(inst, irc, user, channel, False)

    account = irc.dbstore.get_user(user.account)
    if account is not None and account.isadmin():
        return True

    ch_res = wl_generic.check(irc.servname, user.mask, user.account, channel)

    if ch_res == 'ignore':
        return True

    ch_res = inst.check(irc.servname, user.mask, user.account, channel)
    if ch_res == 'ignore':
        return True

    return False


def read_conf():
    pass


def save_conf():
    pass


def trigger_delete_channel(result, args, kwargs):
    network = args[0].name()
    channel = args[1].lower()
    for group_name in groups:
        group = eval(group_name)
        if network in group and channel in group[network]:
            del group[network][channel]
    return result
simpbot.dbstore.dbstore.add_trigger('post', 'drop_chan', trigger_delete_channel)


class conf(object):

    def default_conf(cls):
        default_conf = {}
        default_conf[1] = {
            'clon': {
                'warn_msg': 'warning clon',
                'kick_msg': 'kick clon',
                'final_warn': None,
                'duration': 60 * 60 * 24,
                'status': True,

                'limit': 2,
                'meta': {},

                'actions': {
                    'on_below': [],
                    'on_limit': [('msg', ('{channel}', 'warn_msg'))],
                    'on_exceed': [('ban', ('{channel}', '*!*@{user.host}'))],
                }
            }
        }

        default_conf[2] = {
            'badwords': {
                'warn_msg': 'warning badwords',
                'kick_msg': 'kick badwords',
                'final_warn': None,
                'duration': 60 * 60 * 24,
                'status': True,

                'limit': 2,
                'meta': {
                    'seps': '/-\., ',
                    'lang': {
                        'ES': [
                            '[ck]o[ñ]o',
                            'puth?([ao40]|[i1]th?[aou40]?)(?!dor|cio)',
                            'm[a4][rl]d[i1]th?[ao40]',
                            'm[i1]erd',
                            'jod[ie1]',
                            'gu?e[vb][ioa40]',
                            't[o0]t[o0]n[a4]',
                            '[ck]u[ck][ao40]?',
                            '[vb][a4][gj][i1]n[a4]',
                            'pene(?!lope)',
                            'mete?mel[ao40]',
                            '[sc]hup[a4]',
                            'mama(r|[l[oa40])',
                            '[ck][o0][jg](e|[i1](d[a4])?)',
                            '[sz]emen',
                            't(he)?th?[a4]',
                            '[vb][a4][i1]n([a4]|er[o0])',
                            'p[o0]rn',
                            '[a4]n[a4]l$',
                            #'th?onth?[aoe]',
                            'm[a4]r[i1][cqk]',
                            #'gaf[ao]',
                            #'esth?upid',
                            '[i1]d[i1][o0]t',
                            'mmg[vb]', 'qk', 'hdp', 'mrk', 'mmlo'
                            #'pendej',
                            '([q|[ck]u)l[oe0]',
                            '[bv]ergu?[eai41]',
                            'ere[ckpt][csz]?[i1]?([o0]|[ó])',
                            'p[a4]r[a4]r?mel[o0]',
                            #'coito',
                            'sex',
                            '(\+|m[a4]s)th?ur[bv]',
                            'p[a4]j([a4]|er[ao40])(?!ro)',
                            '[hg]ent[a4][i1]',
                            'f[o0][ly][a4]r']
                    },

                'actions': {
                    'on_below': [('kick', ('{channel}', '{user.nick}', 'kick_msg'))],
                    'on_limit': [('ban', ('{channel}', '*!*@{user.host}'))],
                    'on_exceed': [],
                    }
                }
            }
        }

        default_conf[3] = {
            'stupids': {
                'warn_msg': 'warning stupid',
                'kick_msg': 'kick stupid',
                'final_warn': 'final warn',
                'duration': 60 * 60 * 12,
                'status': True,

                'limit': 2,
                'meta': {'chars': 30},

                'actions': {
                    'on_below': [('msg', ('{channel}', 'warn_msg'))],
                    'on_limit': [
                        ('msg', ('{user.nick}', 'final warn')),
                        ('kick', ('{channel}', '{user.nick}', 'kick_msg'))],
                    'on_exceed': [('ban', ('{channel}', '*!*@{user.host}'))],
                }
            }
        }

        default_conf[4] = {
            'repeat': {
                'warn_msg': 'warning repeat',
                'kick_msg': 'kick repeat',
                'final_warn': 'final warn',
                'duration': 60 * 60 * 12,
                'status': True,

                'limit': 3,
                'meta': {'chars': 8},

                'actions': {
                    'on_below': [('msg', ('{channel}', 'warn_msg'))],
                    'on_limit': [
                        ('msg', ('{user.nick}', 'final warn')),
                        ('kick', ('{channel}', '{user.nick}', 'kick_msg'))],
                    'on_exceed': [('ban', ('{channel}', '*!*@{user.host}'))],
                }
            }
        }

        default_conf[5] = {
            'upper': {
                'warn_msg': 'warning upper',
                'kick_msg': 'kick upper',
                'final_warn': None,
                'duration': 60 * 60 * 12,
                'status': True,

                'limit': 3,
                'meta': {
                    'percent': 75.0,  # percentage
                    'length': 4
                },

                'actions': {
                    'on_below': [('msg', ('{channel}', 'warn_msg'))],
                    'on_limit': [
                        ('msg', ('{user.nick}', 'final warn')),
                        ('kick', ('{channel}', '{user.nick}', 'kick_msg'))],
                    'on_exceed': [('ban', ('{channel}', '*!*@{user.host}'))]
                }
            }
        }

        default_conf[6] = {
            'link': {
                'warn_msg': 'warning link',
                'kick_msg': 'kick link',
                'final_warn': 'final link',
                'duration': 60 * 60 * 12,
                'status': True,

                'limit': 2,
                'meta': {
                    'links': [
                        #'(.+)?https?://((www)(\.))?(fb|facebook)\.com/?(.+)?',
                        '(.+)?https?://((www)(\.))?xvideos\.com/?(.+)?',
                        '(.+)?https?://((www)(\.))?xnxx\.com/?(.+)?',
                        '(.+)?https?://((www)(\.))?xxxymovies\.com/?(.+)?',
                        '(.+)?https?://((www)(\.))?xbef\.com/?(.+)?',
                        '(.+)?https?://((www)(\.))?sexu\.com/?(.+)?',
                        '(.+)?https?://((www)(\.))?xnxx\.com/?(.+)?',
                        '(.+)?https?://((www)(\.))?mofosex\.com/?(.+)?',
                        '(.+)?https?://((www)(\.))?anysex\.com/?(.+)?',
                        '(.+)?https?://((www)(\.))?foxgay\.com/?(.+)?',
                        '(.+)?https?://((www)(\.))?xhamster\.com/?(.+)?',
                        '(.+)?https?://((www)(\.))?anysex\.com/?(.+)?',
                        #'(.+)?https?://((www)(\.))?twitter\.com/?(.+)?',
                    ]
                },

                'actions': {
                    'on_below': [('msg', ('{channel}', 'warn_msg'))],
                    'on_limit': [
                        ('msg', ('{user.nick}', 'final warn')),
                        ('kick', ('{channel}', '{user.nick}', 'kick_msg'))],
                    'on_exceed': [('ban', ('{channel}', '*!*@{user.host}'))],
                }
            }
        }

        default_conf[7] = {
            'flood': {
                'warn_msg': 'warning flood',
                'kick_msg': 'kick flood',
                'final_warn': 'final warn',
                'duration': 60 * 60 * 12,
                'status': True,

                'limit': 3,
                'meta': {
                    "send": 4,
                    "time": 30},

                'actions': {
                    'on_below': [('msg', ('{channel}', 'warn_msg'))],
                    'on_limit': [
                        ('msg', ('{user.nick}', 'final warn')),
                        ('kick', ('{channel}', '{user.nick}', 'kick_msg'))],
                    'on_exceed': [('ban', ('{channel}', '*!*@{user.host}'))],
                }
            }
        }

    def __init__(self, network):
        self.network = network
        self.channel_stack = {}

    def has_channel(self, channel):
        return channel in self.channel_stack

    def set(self, channel, config=None):
        if not self.network in main_conf:
            main_conf[self.network] = self.channel_stack

        if self.has_channel(channel):
            raise ValueError('Channel "%s" in %s %s already registered' % (channel, self.network))

        config = config or self.default_conf()
        channel = Channel(self.network, channel, config)
        self.channel_stack[channel.channel] = channel
        save_conf()


class Channel(object):
    __handlers = {}

    def set_handler(cls, name, HandlerObj):
        cls.__handlers[name] = HandlerObj

    def get_handler(cls, name):
        return cls.__handlers[name]

    def has_handler(cls, name):
        return name in cls.__handlers

    def del_handler(cls, name):
        del cls.__handlers[name]

    def __init__(self, network, channel, config):
        self.network = network
        self.channel = channel
        self.config = config
        self.handlers = {}

    def __getitem__(self, level):
        return self.config[level]

    def __setitem__(self, level, value):
        self.config[level] = value
        save_conf()

    def getLevels(self):
        levels = list(self.config.keys())
        levels.sort()
        return levels

    def change_levels(self, p1, p2):
        self.config[p1], self.config[p2] = self.config[p2], self.config[p1]


class BaseHandler(object):

    def __init__(self, irc, channel, config):
        self.config = config
        self.irc = irc
        self.request = irc.request
        self.channel = irc.request.get_chan(channel)

    def __getitem__(self, key):
        try:
            return self.config[key]
        except KeyError:
            return self.config['meta'][key]

    def __setitem__(self, key, value):
        if key in self.config:
            self.config[key] = value
        elif key in self.config['meta']:
            self.config['meta'][key] = value
        save_conf()

    def __getattr__(self, attr_name):
        try:
            return self[attr_name]
        except KeyError:
            raise AttributeError("%s has no attribute '%s'" % (
                self.__class__.__name__, attr_name))

    def __setattr__(self, key, value):
        if key in self.config:
            self.config[key] = value
        elif key in self.config['meta']:
            self.config['meta'][key] = value
        save_conf()

    def process(self):
        if self.status is False:
            return
        self._process()


class ClonHandler(BaseHandler):

    def clones(self, user):
        clones = [user]
        if in_whitelist(wl_clon, self.irc, user, channel.channel_name):
            return clones

        for usr in self.channel.users:
            if usr.host == user.host and not usr in clones:
                clones.append(usr)
        return clones

    def _process(self):
        for user in self.channel.users:
            clones = self.clones(user)
            if len(clones) < self.limit: