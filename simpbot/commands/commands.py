# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import Queue
import re
import time
import requeries
from simpbot import modules
from simpbot import parser
from simpbot.bottools.dummy import thread
from simpbot.bottools.irc import color
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
        self.queue = Queue.Queue()
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
        except Queue.Empty:
            return

    def check_generic(self, user, instance, level):
        res = instance.check(self.irc.servname, user=user.account)

        if res == 'allow':
            action = allow  # Buen chico...
        elif res == 'deny':
            action = deny  # Oh oh!! Chico malo :)
        elif res == 'ignore':
            action = ignore
        else:
            action = allow

        # Veamos si se encuentra registrado...
        dbuser = self.dbstore.get_user(user.account)
        if dbuser is None:
            return action
        if dbuser.locked:
            if not dbuser.isadmin:
                return locked
            elif dbuser.admin.has_capab(self.overrest['locked']):
                return allow  # Resulta que es administrador...
            else:
                return locked

        elif action is True:
            # ¿ya no hay nada que hacer?
            return allow

        elif action is False:
            if not dbuser.isadmin:
                return deny
            elif dbuser.admin.has_capab(self.overrest[level]):
                return allow  # Resulta que es administrador...
            else:
                return deny

        elif action is None:
            if level == 'global':
                capab = 'over-restriction:ignore global'
            elif level == 'module':
                capab = 'over-restriction:ignore module'
            elif level == 'command':
                capab = 'over-restriction:ignore module'

            if not dbuser.isadmin:
                return ignore
            elif dbuser.admin.has_capab(self.overrest[capab]):
                return allow  # Resulta que es administrador...
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
                # Veamos si se encuentra registrado...
                dbuser = self.dbstore.get_user(user.account)
                if dbuser is None:
                    return allow
                elif dbuser.locked():
                    if not dbuser.isadmin:
                        return locked
                    elif dbuser.admin.has_capab(self.overrest['locked']):
                        return allow  # Resulta que es administrador...
                    else:
                        return locked
                else:
                    return allow

            if not checkaccount:
                return allow

            # ¿Quizás esté bloqueado? Pero no tiene cuenta, puede ser que...
            # ¿su data no esté completa ó actualizada?
            self.request.request(user.nick)
            if not user.completed:
                try:
                    self.request.user(user.nick, timeout=self.irc.timeout)
                except ValueError:
                    return ignore  # Timeout

            # No, nada... No tiene cuenta:)
            if user.account is None:
                return allow

            # Espera... sí estoy aquí es porque sí tiene cuenta!!! :O
            return self.check_generic(user, inst, level)

        elif res == 'deny':
            if user.account is not None:
                # Veamos si se encuentra registrado...
                dbuser = self.dbstore.get_user(user.account)
                if dbuser is None:
                    return deny
                elif dbuser.locked():
                    if not dbuser.isadmin:
                        return locked
                    elif dbuser.admin.has_capab(self.overrest['locked']):
                        return allow  # Resulta que es administrador...
                    else:
                        return locked
                elif not dbuser.isadmin:
                    return deny
                elif dbuser.admin.has_capab(self.overrest[level]):
                    return allow  # Resulta que es administrador...
                else:
                    return deny

            if not checkaccount:
                return deny

            # ¿Quizás esté bloqueado? Pero no tiene cuenta, puede ser que...
            # ¿su data no esté completa ó actualizada?
            self.request.request(user.nick)
            if not user.completed:
                self.request.user(user.nick)

            # No, nada... No tiene cuenta:)
            if user.account is None:
                return deny

            # ¿Espera? sí estoy aquí es porque sí tiene cuenta!!! :O
            return self.check_generic(user, inst, level)

        elif res == 'ignore':
            if user.account is not None:
                # Veamos si se encuentra registrado...
                dbuser = self.dbstore.get_user(user.account)
                if dbuser is None:
                    return ignore
                elif dbuser.locked():
                    if not dbuser.isadmin():
                        return locked
                    elif dbuser.admin.has_capab(self.overrest['locked']):
                        return allow  # Resulta que es administrador...
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
                    return allow  # Resulta que es administrador...
                else:
                    return ignore

            if not checkaccount:
                return ignore

            # ¿Quizas este bloqueado? Pero no tiene cuenta, puede ser que...
            # ¿su data no este completa ó actualizada?
            self.request.request(user.nick)
            if not user.completed:
                self.request.user(user.nick)

            # No, nada... No tiene cuenta:)
            if user.account is None:
                return ignore

            # ¿Espera? sí estoy aquí es porque sí tiene cuenta!!! :O
            return self.check_generic(user, inst, level)

    @thread
    def process(self, match):
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

        status = self.check(user, channel, modules, 'global', True)
        if status == locked:
            if sre:
                msg = 'usted se encuentra ' + color('bloqueado', 'b')
                msg += ', por lo tanto no tiene habilitado el uso del bot. '
                msg += color('Razon de bloqueo:', 'b') + ' "%s", '
                msg += color('Fecha:', 'b') + ' "%s", '
                msg += color('Administrador:', 'b') + ' "%s".'
                usr = self.dbstore.get_user(user.account)
                dat = time.localtime(usr.status[1])
                dat = '%s/%s/%s %s:%s:%s' % (dat.tm_year, dat.tm_mon,
                    dat.tm_mday, dat.tm_hour, dat.tm_min, dat.tm_sec)
                msg = msg % (usr.status[0], dat, usr.status[2])
                self.irc.error(user.nick, msg)
            return
            pass  # Colocar "te encuentras bloqueado"
        elif status is deny or status is ignore:
            return

        _ = parser.replace(self.irc, match)
        _.extend(locals())
        msg = 'Modulo: "{}"; Comando: "{}"; %s'

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
                watchdog = requeries.get(need)
                if not watchdog:
                    msg = msg % 'Solicitó un requerimiento inválido: "%s".'
                    logging.error(msg % need)
                    continue

                if watchdog[0](locals()):
                    return

            handler(self.irc, match, None, target, channel, _)

        if not sre and not privbot:
            return

        msg = 'Modulo: "{}"; Comando: "{}"; %s'
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
                watchdog = requeries.get(need)

                if not watchdog:
                    msg = msg % 'Solicitó un requerimiento inválido: "%s".'
                    logging.error(msg % need)
                    continue

                var['watchdog'] = watchdog
                if watchdog[0](var):
                    logging.debug(msg % 'No cumple con los requerimientos: ' + repr(watchdog))
                    return

            _.addmatch(result)
            handler(self.irc, match, result, target, channel, _)

    @thread
    def loop(self):
        while True:
            if self.irc.connection_status == 's':
                break
            match = self.get()
            if match is None:
                continue
            self.process(match)
