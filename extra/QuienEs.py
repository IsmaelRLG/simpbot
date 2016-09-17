# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import re
import time
import simpbot
from os import path
from os import remove

REGEX = simpbot.parser.ParserRegex('!{date} !{autor} !{message}+')
REGEX = re.compile(REGEX.string)
FORM = "[%d/%m/%Y][%H:%M:%Y] {autor} {message}"
data = simpbot.envvars.data.new_wa('Quien Es')
LIMIT = 380


class whois:

    def __init__(self, nickname):
        self.path = data.join(nickname)
        self.lines = []
        self.full_data = []
        self.read()

    def read(self):
        if not path.exists(self.path):
            return

        data = file(self.path, 'r')
        read = data.read()
        if len(read) == 0:
            return
        data.close()

        for line in read.splitlines():
            self.lines.append(REGEX.match(line).group('message'))
            self.full_data.append(line)

    def write(self, autor, message):
        message = message.rstrip(' ')
        message = message.replace(',', '')

        total = len('. '.join(self.lines))
        total += len(message)
        if len(self.lines) != 0:
            total += 2

        if total > LIMIT:
            return False

        line = FORM.format(autor=autor, message=message)
        self.lines.append(message)
        self.full_data.append(time.strftime(line))
        self.save()
        return True

    def save(self):
        with file(self.path, 'w') as data:
            to_write = '\n'.join(self.full_data)
            data.write(to_write)
        if len(to_write) == 0:
            remove(self.path)

    def remove(self, message):
        for line in self.full_data:
            if REGEX.match(line).group('message') == message:
                self.full_data.remove(line)
                self.lines.remove(message)
                self.save()
                return True
        return False


@simpbot.commands.addCommand('quien es !{nick}', 'quien es quien?', 'quien es')
def whoisget(irc, ev, result, target, channel, _):
    whoismsg = ', '.join(whois(_['nick'].lower()).lines)
    if len(whoismsg) == 0:
        irc.msg(target, _('No se quien es {nick}'))
    else:
        _['whoismsg'] = whoismsg
        irc.msg(target, _('{nick} es {whoismsg}'))


@simpbot.commands.addCommand('!{nick} el(la)? es !{texto}+',
    'Define quien es alguien', 'ella/el es')
def whoisset(irc, ev, result, target, channel, _):
    if whois(_['nick'].lower()).write(_['mask'], _['texto']):
        irc.msg(target, _('Entendido! {nick} es {texto}'))
    else:
        irc.msg(target, _('Ya se muchas cosas de {nick}'))


@simpbot.commands.addCommand('!{nick}( ella|el)? no es !{texto}+',
    'Elimina algo de alguien', 'ella/el no es')
def whoisdel(irc, ev, result, target, channel, _):
    if whois(_['nick'].lower()).remove(_['mask'], _['texto']):
        irc.msg(target, _('Entendido! {nick} ya no es {texto}'))
    else:
        irc.msg(target, _('Yo no sabia eso de {nick}'))


@simpbot.commands.addCommand('info !{nick}',
    'Muestra la informacion completa de alguien', 'info')
@simpbot.commands.admin
def whoisfull(irc, ev, result, target, channel, _):
    irc.msg(target, _('informacion completa de {nick}'))
    if len(whois(_['nick']).full_data) == 0:
        irc.error(target, _('No hay informacion para {nick}'))
        return

    for line in whois(_['nick']).full_data:
        irc.msg(target, line)
