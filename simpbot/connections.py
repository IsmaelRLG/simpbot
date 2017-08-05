# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

from re import compile
from os import path
from six.moves import _thread
from six.moves import configparser
from . import envvars
from .irc import client
from .dbstore import dbstore
from .request import manager
from .commands import ProccessCommands
from .bottools import text
from .bottools import dummy
from . import localedata
import logging

i18n = localedata.get()
regex = compile('^(recv|send)\((.+)\)')
logging = logging.getLogger('simpbot')


def add(core, path, network, rchan, ruser, maxu, maxc, *args, **kwargs):
    network = network.lower()
    if network in core:
        logging.warning(i18n['network duplicated'], network)
        return False
    irc = client(network, *args, **kwargs)
    irc.dbstore = dbstore.dbstore(network, maxc, maxu, rchan, ruser)
    irc.request = manager.manager(irc)
    irc.commands = ProccessCommands(irc)
    irc.conf_path = path
    core[network] = irc
    return True


@text.lower
def get(network):
    if not network in envvars.networks:
        return
    return envvars.networks[network]


@text.lower
def remove(network):
    if not network in envvars.networks:
        return False
    irc_ = envvars.networks[network]
    if irc_.connected:
        irc_.disconnect()
    del envvars.networks[network]


def load_server(abspath, core=envvars.networks, connect=True, attempts=0):
    if not path.isfile(abspath):
        return

    if path.basename(abspath).split('.', 1).pop() != 'ini':
        return

    sections = ['user', 'server', 'simpbot', 'database']
    options = {
        'user': ['nick', 'user'],
        'nickserv': ['sasl', 'username', 'password'],
        'server': ['network', 'address', 'port'],
        'simpbot': ['autoconnect', 'prefix', 'wtime', 'msgps', 'timeout'],
        'database': ['chanregister', 'userregister']}

    conf = configparser.ConfigParser(**envvars.cfg_kwargs)
    conf.read(abspath)

    for section in sections:
        if dummy.invalid_section(conf, section, options[section]):
            logging.error(i18n['bad config'], abspath)
            return

    nick = conf.get('user', 'nick')
    user = conf.get('user', 'user')

    nickserv = None
    sasl = None
    if conf.has_section('nickserv'):
        if not dummy.invalid_section(conf, 'nickserv', options['nickserv']):
            sasl = conf.getboolean('nickserv', 'sasl')
            nickserv = [
                conf.get('nickserv', 'username'),
                conf.get('nickserv', 'password')
            ]

    network = conf.get('server', 'network')
    address = conf.get('server', 'address')
    port = conf.get('server', 'port')
    if conf.has_option('server', 'password'):
        password = conf.get('server', 'password')
    else:
        password = None

    autoconnect = conf.getboolean('simpbot', 'autoconnect')
    plaintext = {}
    for opt in conf.get('simpbot', 'plaintext').split():
        result = regex.findall(opt)
        if len(result) == 0:
            continue

        plaintext[result[0][0]] = result[0][1].split(',')

    prefix = conf.get('simpbot', 'prefix')
    msgps = conf.getfloat('simpbot', 'msgps')
    timeout = conf.getint('simpbot', 'timeout')
    wtime = conf.getint('simpbot', 'wtime')
    if conf.has_option('simpbot', 'default_lang'):
        lang = conf.get('simpbot', 'default_lang')
        if not localedata.simplocales.exists(lang, 'fullsupport'):
            lang = envvars.default_lang
    else:
        lang = envvars.default_lang

    chanregister = conf.get('database', 'chanregister')
    userregister = conf.get('database', 'userregister')
    if conf.has_option('database', 'maxusers'):
        maxusers = conf.getint('dabase', 'maxusers')
    else:
        maxusers = 0
    if conf.has_option('database', 'maxchans'):
        maxchans = conf.getint('dabase', 'maxchans')
    else:
        maxchans = 0

    kwargs = {}
    kwargs['nickserv']  = nickserv
    kwargs['sasl']      = sasl
    kwargs['timeout']   = timeout
    kwargs['msgps']     = msgps
    kwargs['wtime']     = wtime
    kwargs['servpass']  = password
    kwargs['prefix']    = prefix
    kwargs['lang']      = lang
    kwargs['plaintext'] = plaintext

    if not add(core, abspath, network, chanregister, userregister, maxusers,
        maxchans, address, port, nick, user, **kwargs):
        return

    network = network.lower()
    if autoconnect:
        if not connect:
            core[network].autoconnect = True
            return
        _thread.start_new(core[network].try_connect, (attempts,), {})


def load_servers(core=envvars.networks, connect=True, attempts=0):
    for servercfg in envvars.servers.listdir():
        servercfg = envvars.servers.join(servercfg)
        if not envvars.servers.isfile(servercfg):
            continue
        try:
            load_server(servercfg, core, connect, attempts=attempts)
        except Exception as e:
            msg = 'Configuracion "%s" inválida (ERROR: %s).'
            logging.error(msg, servercfg, repr(e))
