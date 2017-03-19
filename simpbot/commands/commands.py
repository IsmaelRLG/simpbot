# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import re
import time
from . import requires
from six.moves import queue
from simpbot import modules
from simpbot import envvars
from simpbot import parser
from simpbot import localedata
from simpbot.bottools.dummy import thread

i18n = localedata.get()
logging = __import__('logging').getLogger('commands')

allow = True
deny = False
locked = 0
ignore = None


class ProccessCommands:
    overrest = {
        'global': 'over-restriction:deny global',
        'module': 'over-restriction:deny module',
        'command': 'over-restriction:deny command',
        'ig_global': 'over-restriction:ignore global',
        'ig_module': 'over-restriction:ignore module',
        'ig_command': 'over-restriction:ignore command',
        'locked': 'over-restriction:lock user'}

    def __init__(self, irc, timeout=60):
        self.irc = irc
        self.timeout = timeout
        self.queue = queue.Queue()
        self.loop()

    @property
    def dbstore(self):
        return self.irc.dbstore

    @property
    def request(self):
        return self.irc.request

    @staticmethod
    def get_command(text, noregex=True, regex=True, first=False):
        commands = []
        for modname, module in modules.core.items():
            for hanname, handler in module.handlers.items():
                if handler.regex is None:
                    if noregex:
                        commands.append((handler, None))
                    continue
                elif regex:
                    result = handler.match(text)
                    if result:
                        commands.append((handler, result))
                        if first:
                            return commands
                    continue
        return commands

    def put(self, item):
        self.queue.put(item)

    def get(self):
        try:
            return self.queue.get(timeout=self.timeout)
        except queue.Empty:
            return

    def check_generic(self, user, instance, level):
        res = instance.check(self.irc.servname, user=user.account)

        if res == 'allow':
            action = allow
        elif res == 'deny':
            action = deny
        elif res == 'ignore':
            action = ignore
        else:
            action = allow

        dbuser = self.dbstore.get_user(user.account)
        if dbuser is None:
            return action
        if dbuser.locked:
            if dbuser.isadmin is None:
                return locked
            elif dbuser.admin.has_capab(self.overrest['locked']):
                return allow
            else:
                return locked

        elif action is True:
            return allow

        elif action is False:
            if dbuser.isadmin is None:
                return deny
            elif dbuser.admin.has_capab(self.overrest[level]):
                return allow
            else:
                return deny

        elif action is None:
            if level == 'global':
                capab = 'over-restriction:ignore global'
            elif level == 'module':
                capab = 'over-restriction:ignore module'
            elif level == 'command':
                capab = 'over-restriction:ignore module'

            if dbuser.isadmin is None:
                return ignore
            elif dbuser.admin.has_capab(self.overrest[capab]):
                return allow
            else:
                return ignore

    def check(self, user, channel, inst, level='global', checkaccount=False):
        # return:
        #     True -> allow
        #     False -> deny
        #     None -> locked

        res = inst.check(self.irc.servname, user.mask, user.account, channel)
        if res == 'allow':
            if user.account is not None:
                dbuser = self.dbstore.get_user(user.account)
                if dbuser is None:
                    return allow
                elif dbuser.locked():
                    if not dbuser.isadmin:
                        return locked
                    elif dbuser.admin.has_capab(self.overrest['locked']):
                        return allow
                    else:
                        return locked
                else:
                    return allow

            if not checkaccount:
                return allow

            self.request.request(user.nick)
            if not user.completed:
                try:
                    self.request.user(user.nick, timeout=self.irc.timeout)
                except ValueError:
                    return ignore

            if user.account is None:
                return allow

            return self.check_generic(user, inst, level)

        elif res == 'deny':
            if user.account is not None:
                dbuser = self.dbstore.get_user(user.account)
                if dbuser is None:
                    return deny
                elif dbuser.locked():
                    if not dbuser.isadmin:
                        return locked
                    elif dbuser.admin.has_capab(self.overrest['locked']):
                        return allow
                    else:
                        return locked
                elif not dbuser.isadmin:
                    return deny
                elif dbuser.admin.has_capab(self.overrest[level]):
                    return allow
                else:
                    return deny

            if not checkaccount:
                return deny

            self.request.request(user.nick)
            if not user.completed:
                self.request.user(user.nick)

            if user.account is None:
                return deny

            return self.check_generic(user, inst, level)

        elif res == 'ignore':
            if user.account is not None:
                dbuser = self.dbstore.get_user(user.account)
                if dbuser is None:
                    return ignore
                elif dbuser.locked():
                    if not dbuser.isadmin():
                        return locked
                    elif dbuser.admin.has_capab(self.overrest['locked']):
                        return allow
                    else:
                        return locked

                if level == 'global':
                    capab = 'over-restriction:ignore global'
                elif level == 'module':
                    capab = 'over-restriction:ignore module'
                elif level == 'command':
                    capab = 'over-restriction:ignore module'

                if not dbuser.isadmin():
                    return ignore
                elif dbuser.admin.has_capab(self.overrest[capab]):
                    return allow
                else:
                    return ignore

            if not checkaccount:
                return ignore

            self.request.request(user.nick)
            if not user.completed:
                self.request.user(user.nick)

            if user.account is None:
                return ignore

            return self.check_generic(user, inst, level)

    def get_lang(self, user, channel):
        if user.account is None:
            if channel is not None and self.dbstore.has_chan(channel):
                return self.dbstore.get_chan(channel)
            else:
                return self.irc.default_lang
        else:
            dbuser = self.dbstore.get_user(user.account)
            if dbuser is None:
                if channel is not None and self.dbstore.has_chan(channel):
                    return self.dbstore.get_chan(channel)
                else:
                    return self.irc.default_lang
            else:
                return dbuser.default_lang

    @thread
    def process(self, match, regexonly=False):
        self._process(match, regexonly)

    def _process(self, match, regexonly=False):
        user = self.request.set_user(*match.group('user', 'host', 'nick'))
        irc = self.irc
        completeline = match.string  # lint:ok
        channel = None
        privbot = False
        target = user.nick
        sendin = match.group('target')
        message = match.group('message')

        if user.nick.lower() == irc.nickname.lower():
            return
        elif sendin.lower() == irc.nickname.lower():
            privbot = True
        else:
            channel = sendin
            target = channel

        regex = '^({}([:;, ] ?)|[{}])(?P<text>.*)'
        regex = regex.format(re.escape(irc.nickname), re.escape(irc.prefix))
        cmd = message

        if privbot:
            sre = None
        else:
            sre = re.match(regex, message, re.IGNORECASE)
            if sre:
                cmd = sre.group('text')

        lang = self.get_lang(user, channel)
        status = self.check(user, channel, modules, 'global', True)
        if status == locked:
            if sre or privbot:
                msg = localedata.get(lang)['you are locked']
                usr = self.dbstore.get_user(user.account)
                dat = time.localtime(usr.status[1])
                dat = '%s/%s/%s %s:%s:%s' % (dat.tm_year, dat.tm_mon,
                    dat.tm_mday, dat.tm_hour, dat.tm_min, dat.tm_sec)
                msg = msg % (usr.status[0], dat, usr.status[2])
                self.irc.error(user.nick, msg)
            return
        elif status is deny or status is ignore:
            return

        _ = parser.replace(self.irc, match)
        _.extend(locals())

        msg = i18n['command info']
        if not regexonly:
            # Se procesan comandos sin regex...
            for handler, result in self.get_command(None, regex=False):
                msg = msg.format(handler.mod_name, handler.name)
                module = handler.module

                if module is not None:
                    status = self.check(user, channel, module, 'module', False)
                    if status is deny or status is ignore:
                        continue

                status = self.check(user, channel, handler, 'command', False)
                if status is deny or status is ignore:
                    continue

                for need in handler.need:
                    watchdog = requires.get(need)
                    if not watchdog:
                        logging.error(msg % i18n['invalid requirements'] % need)
                        continue

                    if watchdog[0](locals()):
                        return

                if handler.i18n:
                    loader = handler.i18n['loader']
                    locale = loader.getfull(lang, handler.mod_name)
                else:
                    locale = None
                handler(self.irc, match, None, target, channel, _, locale)
                if handler.rec_form:
                    abspath = envvars.records.join(handler.fullname)
                    with open(abspath, 'a') as fp:
                        fp.write(_(handler.rec_form, include_time=True) + '\n')

        if not sre and not privbot:
            return

        msg = i18n['command info']
        # Se procesan comandos con regex...
        for handler, result in self.get_command(cmd, noregex=False, first=True):
            msg = msg.format(handler.mod_name, handler.name)
            module = handler.module
            if module is not None:
                status = self.check(user, channel, module, 'module', False)
                if status is deny or status is ignore:
                    continue

            status = self.check(user, channel, handler, 'command', False)
            if status is deny or status is ignore:
                continue

            var = locals()
            for need in handler.need:
                watchdog = requires.get(need)

                if not watchdog:
                    logging.error(msg % i18n['invalid requirements'] % need)
                    continue

                var['watchdog'] = watchdog
                if watchdog[0](var):
                    return

            _.addmatch(result)
            if handler.i18n:
                loader = handler.i18n['loader']
                locale = loader.getfull(lang, handler.mod_name)
            else:
                locale = None
            handler(self.irc, match, result, target, channel, _, locale)
            if handler.rec_form:
                with open(envvars.records.join(handler.fullname), 'a') as fp:
                    fp.write(_(handler.rec_form, include_time=True) + '\n')

    @thread
    def loop(self):
        while True:
            if self.irc.connection_status == 's':
                break
            match = self.get()
            if match is None:
                continue
            self.process(match)
