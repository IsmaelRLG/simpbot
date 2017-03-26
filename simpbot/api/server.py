# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

from __future__ import unicode_literals
from flask import Flask, request, jsonify, abort
from simpbot import envvars
from simpbot import localedata
from simpbot.irc import client
from simpbot.commands import ProccessCommands
from simpbot.bottools import text
from simpbot.connections import get as get_connection
from simpbot.connections import load_servers
from simpbot.localedata import get as get_locale
from simpbot.admins import get_admin, has_admin
from six import string_types as string
from six.moves import _thread
from types import NoneType
from . import config

import time, threading
logging = __import__('logging').getLogger('api')
i18n = get_locale(package='simpbot.commands.commands')
locale = get_locale()


class commands(ProccessCommands):

    def __init__(self, irc):
        super(commands, self).__init__()
        self.irc = irc

    def process(self, message):
        match = client.regexmsg(':%s!~api@%s PRIVMSG %s :%s' % (
            self.irc.nickapi,
            self.irc.hostname,
            self.irc.nickname,
            message))

        user = self.request.set_user(*match.group('user', 'host', 'nick'))
        user.account = '401.api.' + self.irc.nickapi
        irc = self.irc
        if not self.dbstore.has_user(user.account):
            self.dbstore.register_user(user.account)
            usr = self.dbstore.get_user(user.account)
            irc._verbose('api', locale['new user'] % (user.account))
        else:
            usr = self.dbstore.get_user(user.account)

        if not usr.isadmin():
            usr.set_admin(self.irc.admin, int(time.time()))
        self._process(match, regexonly=True)


class ircpipe:

    ircattr = [
        'send_raw', 'proccess_handlers', 'try_connect', 'input', 'output',
        'login', 'disconnect', 'reconnect', 'connect', 'set_status', 'ctcp',
        'ctcp_reply', 'join', 'kick', 'invite', 'nick', 'mode', 'passwd',
        'part', 'pong', 'remove', 'who', '_who', 'whois', '_whois', 'topic',
        'user', 'quit', 'dbstore', 'request', 'connected', 'connection_status',
        'input_alive', 'output_alive', 'lock', 'socket', 'input_buffer',
        'output_buffer', 'features', 'default_lang', 'conf_path', 'servname',
        'addr', 'ssl', 'port', 'servpass', 'usens', 'sasl', 'timeout', 'msgps',
        'wtime', 'prefix', 'nickname', 'username']

    def __init__(self, irc, admin, hostname):
        self.irc = irc
        self.admin = admin.user
        self.hostname = 'simpbot-api.%s.%s' % (admin.user, hostname)
        self.nickapi = '401-' + admin.user

        self.commands = commands(self)
        self.apiout = self.commands.queue

    def __del__(self):
        self.irc.__del__()

    def __getattr__(self, attr):
        if attr in self.ircattr:
            return getattr(self.ircattr, attr)
        else:
            return getattr(self, attr)

    def update_attr(self, attr, value):
        setattr(self.irc, attr, value)

    ##########################################################################
    #          toda esta mierda solo para capturar los mensajes...           #
    ##########################################################################

    def _msg(self, target, msg):
        self.irc.notice(target, msg)

    def _verbose(self, capab, text):
        self.irc.verbose(capab, text)

    @text.normalize
    def put(self, *args):
        self.apiout.put(args)

    def privmsg(self, target, msg):
        self.put('privmsg', target, msg)
        if target.lower() != self.nickapi:
            self.irc.privmsg(target, msg)

    def notice(self, target, msg):
        self.put('notice', target, msg)
        if target.lower() != self.nickapi:
            self.irc.notice(target, msg)

    msg = notice

    def verbose(self, capab, text):
        self.put('verbose', capab, text)
        self.irc.verbose(capab, text)

    def error(self, target, msg):
        self.put('error', target, msg)
        if target.lower() != self.nickapi:
            self.irc.error(target, msg)

requires_default = ['username', 'password', 'network']
api = Flask('__main__')


def auth_required(requires=[], capabs=[], use_ircpipe=False):
    requires = requires_default + requires

    def wrap(func):
        def sub(*args, **kwargs):
            host = request.remote_addr
            logging.info('Procesando petición de: %s', host)
            if not request.json:
                return abort(415)

            for keyname in requires:
                if not keyname in request.json:
                    return abort(400)

                val = request.json[keyname]
                if keyname == 'network':
                    if type(val) is NoneType:
                        continue
                    elif isinstance(val, string):
                        request.json['network'] = val.lower()
                    else:
                        print(request.json)
                        return abort(400)
                elif keyname == 'action' and not isinstance(val, string):
                    return abort(400)
                elif request.json[keyname] is None:
                    return abort(400)

            # checking credentials...
            network = request.json['network']
            username = request.json['username'].lower()
            password = request.json['password']

            if not has_admin(network, username):
                # Colocar baneo aquí
                print('No existe!')
                return abort(401)

            admin = get_admin(network, username)
            if not admin.checkpass(password):
                # Colocar baneo aquí
                print('Contraseña invalida..')
                return abort(401)

            if not admin.has_capab('api'):
                # Colocar baneo aquí
                print('Sin capacidades..')
                return abort(401)

            for capab in capabs:
                if not admin.has_capab(capab):
                    return abort(401)

            if use_ircpipe:
                irc = ircpipe(get_connection(network), admin, host)
                irc._verbose('api', locale['logged'] % (username, host))
                request.json['irc'] = irc
            return func(*args, **kwargs)
        sub.__name__ = func.__name__
        return sub
    return wrap


@api.route(config.URL_COMMANDS, methods=['POST'])
@auth_required(['action'], use_ircpipe=True)
def simpbot_api():
    irc = request.json['irc']
    adm = irc.admin
    irc.commands.process(request.json['action'])
    response = {'status': None, 'errors': [], 'messages': [], 'verbose': []}
    while not irc.queue.empty():
        _from, target, message = irc.queue.get()
        if _from == 'error':
            response['errors'].append([target, message])
        elif _from == 'notice' or _from == 'privmsg':
            response['messages'].append([target, message])
        elif _from == 'verbose' and adm.has_capab(target):
            response['verbose'].append(message)

    if len(response['errors']) > 0:
        response['status'] = 'failed'
    else:
        response['status'] = 'success'

    return jsonify(response), 201


@api.route(config.URL_CONNECTIONS, methods=['GET'])
@auth_required()
def connections():
    response = {'status': 'success', 'servers': []}
    parsebool = lambda bool: True if bool else False
    for network_name, ircobj in envvars.networks.items():
        response['servers'].append([
            ircobj.servname,
            ircobj.addr,
            ircobj.port,
            parsebool(ircobj.ssl),
            parsebool(ircobj.sasl),
            parsebool(ircobj.servpass),
            ircobj.connection_status])
    return jsonify(response), 201


@api.route(config.URL_DISCONNECT, methods=['POST'])
@auth_required(['network'], ['disconnect'])
def disconnect():
    response = {'status': None, 'errors': [], 'messages': []}
    network = request.json['network']
    if not network in envvars.networks:
        response['errors'].append(locale['invalid network name'])
        response['status'] = 'failed'
        return jsonify(response), 201

    irc = get_connection(network)
    if not irc.connected:
        response['errors'].append(locale['already disconnected'])
        response['status'] = 'failed'
        return jsonify(response), 201

    irc.disconnect(locale['disconnecting'] % request.json['username'])
    response['message'].append(locale['disconnected'])
    response['status'] = 'success'
    conns = 0
    for ircobj in envvars.networks.values():
        if ircobj.connected:
            conns += 1
    if conns == 0:
        response['message'].append(locale['stoped bot'])
        stop()
    return jsonify(response), 201


@api.route(config.URL_RECONFIGURE, methods=['POST'])
@auth_required(capabs=['reconfigure'])
def reconfigure():
    response = {'status': None, 'messages': [], 'error': {},
        'added': [],
        'removed': [],
        'updated': []}

    vcore = {}
    load_servers(core=vcore, connect=False)

    def add(core_name, network):
        if network in response[core_name]:
            return
        else:
            response[core_name].append(network)

    def diff(irc, ircobj, attr, name):
        reconnect = isinstance(attr, tuple)
        if getattr(irc, attr) != getattr(ircobj, attr):
            setattr(irc, attr, getattr(ircobj, attr))
            add('updated', name)
            if reconnect:
                return True

    if len(vcore) == 0:
        response['message'].append(locale['stoped bot'])
        threading.Timer(15, stop, (), {})
        return jsonify(response), 201

    for name in envvars.networks:
        if not name in vcore:
            irc = envvars.networks[name]
            irc.disconnect(locale['disconnecting'] % request.json['username'])
            del envvars.networks[name]
            add('removed', name)

    chk_diff = [
        'plaintext', 'default_lang', 'autoconnect', 'conf_path', ('addr',),
        ('servpass',), 'nickserv', ('sasl',), 'timeout', ('ssl',), ('port',),
        'msgps', 'wtime', 'prefix', ('username',), 'usens']

    for name, ircobj in vcore.values():
        if name in envvars.networks:
            irc = envvars.networks[name]
            if irc.total_chan() != ircobj.total_chan() or\
                irc.total_user() != ircobj.total_user():
                irc.dbstore = ircobj.dbstore
                add('updated', name)

            if irc.nickname != ircobj.nickname:
                if irc.connected:
                    irc.nick(ircobj.nickname)
                else:
                    irc.nickname = ircobj.nickname

            reconnect = False
            for attr in chk_diff:
                if diff(irc, ircobj, attr, name) and not reconnect:
                    reconnect = True

            if not reconnect:
                continue
            _thread.start_new(irc.reconnect, (
                locale['reconnecting'] % request.json['username'],))
        else:
            envvars.networks[name] = ircobj
            _thread.start_new(ircobj.try_connect, ())
            add('added', name)

    try:
        envvars.cfg.data.clear()
        envvars.cfg.read()
    except ValueError:
        response['error'].append(locale['bad config'])

    if 'DEFAULT_LANT' in envvars.cfg and envvars.cfg['DEFAULT_LANG'] != '' and\
        envvars.cfg['DEFAULT_LANG'].lower() != envvars.default_lang.lower():
        lang = envvars.cfg['DEFAULT_LANG']

        if localedata.simplocales.exists(lang, 'fullsupport'):
            envvars.default_lang = lang
            modnames = [
          # Nombre de modulo                 Atributo
          # ----------------------------     -------------
            ('simpbot.admins',               'i18n'),
            ('simpbot.connections',          'i18n'),
            ('simpbot.handlers',             'i18n'),
            ('simpbot.moduletools.core',     'i18n'),
            ('simpbot.moduletools.hanlders', 'i18n'),
            ('simpbot.commands.requires',    'i18n'),
            ('simpbot.irc',                  'i18n'),
            ('simpbot.commands.commands',    'i18n'),
            ('simpbot.api.server',           'locale'),
            ('simpbot.cli',                  'locale')]
            for modname, attr in modnames:
                try:
                    module = __import__(modname)
                except ImportError:
                    continue
                setattr(module, attr, localedata.get(package=modname))
            response['message'].append(locale['restart simpbot'])
        else:
            response['error'].append(locale['invalid lang'] % lang)

    return jsonify(response), 201


@api.route(config.URL_CONNECT, methods=['POST'])
@auth_required(['network'], ['connect'])
def connect():
    response = {'status': None, 'errors': [], 'messages': []}
    network = request.json['network'].lower()
    if not network in envvars.networks:
        response['errors'].append(locale['invalid network name'])
        response['status'] = 'failed'
        return jsonify(response), 201

    irc = get_connection(network)
    if irc.connected:
        response['errors'].append(locale['already connected'])
        response['status'] = 'failed'
        return jsonify(response), 201

    irc.try_connect(attempt=1)
    if not irc.connected:
        response['errors'].append(locale['can not connect'])
        response['status'] = 'failed'
        return jsonify(response), 201

    response['message'].append(locale['connected'])
    response['status'] = 'success'
    return jsonify(response), 201


@api.route(config.URL_RECONNECT, methods=['POST'])
@auth_required(['network'], ['disconnect', 'connect'])
def reconnect():
    response = {'status': None, 'errors': [], 'messages': []}
    network = request.json['network'].lower()
    if not network in envvars.networks:
        response['errors'].append(locale['invalid network name'])
        response['status'] = 'failed'
        return jsonify(response), 201

    irc = get_connection(network)
    if irc.connected:
        irc.disconnect(locale['reconnecting'] % request.json['username'])

    irc.try_connect(attempt=1)
    if not irc.connected:
        response['errors'].append(locale['can not connect'])
        response['status'] = 'failed'
        return jsonify(response), 201

    response['message'].append(locale['connected'])
    response['status'] = 'success'
    return jsonify(response), 201


def start():
    if envvars.api_started:
        return

    import logging as logger
    log = logger.getLogger('werkzeug')
    log.disabled = 1

    try:
        envvars.api_started = True
        api.run(
            host=config.LISTEN_HOST,
            port=config.LISTEN_PORT,
            threaded=True,
            debug=False)
    except Exception as error:
        envvars.api_started = False
        log.disabled = 0
        raise error
    else:
        log.disabled = 0
        envvars.api_started = False


def stop():
    if not envvars.api_started:
        return

    shutdown = request.environ.get('werkzeug.server.shutdown')
    if shutdown is None:
        return
    shutdown()

    import logging as logger
    log = logger.getLogger('werkzeug')
    log.disabled = 0