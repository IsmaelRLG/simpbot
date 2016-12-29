# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import time
import re
from .envvars import ctrl
from .envvars import networks
from .bottools import text
from .bottools import dummy
from .bottools import irc
global_name = text.randphras()
simp = '([^ ]+) (deny|allow|ignore) (user|chan|mask):([^ ]+)( (\d{1,}))? {0,}[^#]+?'
simp = re.compile(simp)
glob = re.compile('global (deny|allow)( (\d{1,}))?')
comm = re.compile('^#(.+)?')


class control(object):

    def __init__(self, fullname):
        self.status = {}
        self.fullname = fullname
        self.clear()
        self.load()

    def add(self, network, order, type, target, date=None):
        if not network in networks.keys():
            return

        if date is None:
            pass
        elif isinstance(date, basestring):
            if date.isdigit():
                date = int(date)
                if time.time() >= date:
                    return
        elif isinstance(date, int) or isinstance(date, float):
            date = int(date)
        else:
            return

        if type == 'mask':
            if not irc.valid_mask(target):
                return

            target = (re.compile(irc.parse_mask(target)), target)
            for targ, date2 in self.status[network][order][type].items():
                if targ[0].pattern == target:
                    return
        elif type == 'chan':
            if not irc.ischannel(target, network):
                return
        if type != 'user' and target:
            if target in self.status[network][order][type]:
                return
        self.status[network][order][type][target] = date
        return True

    def add_line(self, line):
        match = simp.findall(line)
        if len(match) > 0:
            network, order, type, target, null, date = match[0]
            return self.add(network, order, type, target, date)

    def clear(self):
        self.status.clear()
        for netnam in networks:
            self.status[netnam] = {'deny': {}, 'allow': {}, 'ignore': {}}
            for order in self.status[netnam].keys():
                for type in ('user', 'mask', 'chan'):
                    self.status[netnam][order][type] = {}

    @text.lower
    def remove(self, network, order, type, target):
        if not network in self.status:
            return

        if type == 'mask':
            if not irc.valid_mask(target):
                return
            for targ, date2 in self.status[network][order][type].items():
                if targ[0].pattern == target:
                    del self.status[network][order][type][targ]

        elif target in self.status[network][order][type]:
            del self.status[network][order][type][target]

    def load(self):
        if not ctrl.exists(self.fullname):
            return

        with ctrl.file(self.fullname, 'r') as data:
            lines = data.readlines()

        for line in lines:
            line = line.replace('\n', '').lower()
            if len(line) == 0 or comm.match(line):
                continue
            match = simp.findall(line)
            if len(match) > 0:
                network, order, type, target, null, date = match[0]
                self.add(network, order, type, target, null, date)
                continue

            match = glob.findall(line)
            if len(match) > 0:
                self.add_global(match[0][0], match[0][2])
                continue

    @text.lower
    def add_global(self, order, date=None):
        if not global_name in self.status:
            self.status[global_name] = {}

        if isinstance(date, basestring):
            if date.isdigit():
                date = int(date)
                if time.time() >= date:
                    return
            else:
                return

        self.status['global'][order] = date
        return True

    @text.lower
    def remove_global(self, order):
        if not global_name in self.status:
            return

        del self.status['global'][order]
        if len(self.status[global_name]) == 0:
            del self.status[global_name]

    def save(self):
        data = ctrl.file(self.fullname, 'a')
        data.write(dummy.ascii())

        for name in self.status.keys():
            # name = Network name
            if name == global_name:
                if len(self.status[name]) == 0:
                    continue
                for order, date in self.status[name].items():
                    if date is None:
                        date = ''
                    elif time.time() >= date:
                        del self.status[name][order]
                        continue
                    else:
                        date = ' %s' % date
                    data.write('global {}{}\n'.format(order, date))

            status = self.status[name]
            for order in ('allow', 'deny', 'ignore'):  # Primero los permitidos
                # order == allow / deny / ignore
                ornam = order
                order = status[order]
                for type in order.keys():
                    # type == mask / user / chan
                    tnam = type
                    type = order[type]  # lint:ok
                    for target, date in type.items():
                        if date is None:
                            date = ''
                        elif time.time() >= date:
                            del type[target]
                            continue
                        else:
                            date = ' %s' % date
                        if tnam == 'mask':
                            target = target[1]
                        data.write('{} {} {}:{}{}\n'.format(
                            name, ornam, tnam, target, date))

    @text.lower
    def ext_check(self, netw=None, mask=None, user=None, chan=None, glob=False):
        if global_name in self.status:
            status = self.status[global_name]
            if 'allow' in status:
                if status['allow'] is None:
                    return ('allow', None)
                elif time.time() >= status['allow']:
                    del self.status[global_name]
                else:
                    return ('allow', status['allow'] - time.time())

            elif 'deny' in status:
                if status['deny'] is None:
                    return ('deny', None)
                elif time.time() >= status['deny']:
                    del self.status[global_name]
                else:
                    return ('deny', status['deny'] - time.time())

            elif 'ignore' in status:
                if status['ignore'] is None:
                    return ('ignore', None)
                elif time.time() >= status['ignore']:
                    del self.status[global_name]
                else:
                    return ('ignore', status['ignore'] - time.time())
        if glob:
            return

        # Check arguments
        if netw is None:
            if mask is None and user is None and chan is None:
                raise ValueError('Se necesitan argumentos')
        if mask and not irc.valid_mask(mask):
            raise ValueError("Mascara '%s' invalida" % mask)
        if chan and not irc.ischannel(chan, netw):
            raise ValueError("Canal '%s' invalido" % chan)
        if not netw in networks:
            return

        for name in self.status.keys():
            # name = Network name
            if name == global_name:
                continue
            elif name != netw:
                continue

            status = self.status[name]
            for order in ('allow', 'deny', 'ignore'):  # Primero los permitidos
                # order == allow / deny
                ornam = order
                order = status[order]
                for type in order.keys():
                    # type == mask / user / chan
                    tnam = type
                    type = order[type]  # lint:ok
                    for target, date in type.items():
                        if date is not None and time.time() >= date:
                            del type[target]
                            continue
                        if tnam == 'mask' and mask:
                            if target[0].match(mask):
                                return (ornam, date)
                            continue
                        elif tnam == 'user' and user:
                            if target == user:
                                return (ornam, date)
                            continue
                        elif tnam == 'chan' and chan:
                            if target == user:
                                return (ornam, date)
                            continue
        # No se encontró nada, así que se permite
        return ('allow', None)

    def check(self, netw=None, mask=None, user=None, chan=None, glob=False):
        result = self.ext_check(netw, mask, user, chan, glob)
        if result is None:
            return
        else:
            return result[0]