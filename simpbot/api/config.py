# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

from six.moves import urllib
from simpbot.envvars import cfg

urljoin = urllib.parse.urljoin

URL_BASE = '/simpbot/api/v1.0/'
URL_COMMANDS = urljoin(URL_BASE, 'commands/')
URL_CONNECTIONS = urljoin(URL_BASE, 'connections/')
URL_CONNECT = urljoin(URL_BASE, 'connnect/')
URL_DISCONNECT = urljoin(URL_BASE, 'disconnect/')
URL_RECONNECT = urljoin(URL_BASE, 'reconnect/')
URL_RECONFIGURE = urljoin(URL_BASE, 'reconfigure/')

LISTEN_HOST = cfg.get('LISTEN_HOST', '127.0.0.1')
LISTEN_PORT = cfg.getint('LISTEN_PORT', 51397)
CONNECT_HOST = cfg.get('CONNECT_HOST', LISTEN_HOST)
CONNECT_PORT = cfg.getint('CONNECT_PORT', LISTEN_PORT)
DEFAULT_USER = cfg.get('CONNECT_USER', '')

if DEFAULT_USER == '':
    DEFAULT_USER = None
