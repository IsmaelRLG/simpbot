# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import os
import re
import capab
from admins import admins
from simpbot import envvars
from simpbot.bottools import dummy
from ConfigParser import ConfigParser

logging = __import__('logging').getLogger('admins')
__general_conf = ConfigParser()
__general_conf.read(envvars.adminspath)
regex_local = re.compile('local ([^ ]+) ([^ ]+)')
regex_global = re.compile('global ([^ ]+)')


def add_admin(network, user, hash, capabs, algm='md5',logins=0, maxlogins=0, ison=[],
    conf=None, path=None, save=False, timeout=2419200, verbose=True, account=[]):
    admin = admins(network, user, hash, algm, logins, maxlogins, ison, conf,
        path, timeout, verbose, account)
    name_admin = str(admin)

    if name_admin in envvars.admins:
        logging.warning('Administrador "%s" duplicado.' % name_admin)
        return False
    else:
        envvars.admins[name_admin] = admin

    if isinstance(capabs, basestring):
        capabs = capabs.split(',')
    admin_capabs = capab.gen_capab(*capabs)
    if len(admin_capabs) == 0:
        logging.warning('Administrador "%s" sin capacidades definidas.', name_admin)
        return False

    admin.capab.extend(admin_capabs)

    if conf is None:
        conf = __general_conf
    if path is None:
        path = envvars.adminspath

    admin.conf = conf
    admin.confpath = path

    if not conf.has_section(name_admin):
        admin.save()
    envvars.admins[name_admin] = admin
    logging.info('Administrador "%s" agregado.' % name_admin)


def has_admin(network, user):
    name_admin = '%s %s' % ('local ' + network if network else 'global', user)
    return name_admin in envvars.admins


def get_admin(network, user):
    name_admin = '%s %s' % ('local ' + network if network else 'global', user)
    return envvars.admins[name_admin]


def del_admin(network, user):
    name_admin = '%s %s' % ('local ' + network if network else 'global', user)
    if not name_admin in envvars.admins:
        return
    admin = envvars.admins[name_admin]
    del envvars.admins[name_admin]
    if admin.conf is __general_conf:
        admin.conf.remove_section(name_admin)
        admin.save()
    if admin.confpath != envvars.adminspath:
        if not os.path.exists(admin.confpath):
            return
        elif not os.path.isfile(admin.confpath):
            return
        os.remove(admin.confpath)
    logging.info('Administrador "%s" eliminado.' % name_admin)


def load_admins():
    options = 'password timeout maxlogins verbose capability isonick'.split()

    for admin in __general_conf.sections():
        if dummy.invalid_section(__general_conf, admin, options):
            logging.error('Configuracion de administrador "%s" erronea', admin)
            continue

        result = regex_local.findall(admin)
        if result:
            network = result[0][0]
            user = result[0][1]
        elif regex_global.findall(admin):
            result = regex_global.findall(admin)
            network = None
            user = result[0]
        else:
            logging.error('Configuración de administrador "%s" erronea', admin)
            continue

        password = __general_conf.get(admin, 'password')
        timeout = __general_conf.getint(admin, 'timeout')
        maxlogins = __general_conf.getint(admin, 'maxlogins')
        verbose = __general_conf.getboolean(admin, 'verbose')
        capability = __general_conf.get(admin, 'capability').split(',')
        logins = 0
        if __general_conf.has_option(admin, 'logins'):
            logins = __general_conf.getint(admin, 'logins')
        account = []
        if __general_conf.has_option(admin, 'account'):
            account.extend(__general_conf.get(admin, 'account').lower().split(','))
            while '' in account:
                account.remove('')
        isonick = []
        if __general_conf.has_option(admin, 'isonick'):
            isonick.extend(__general_conf.get(admin, 'isonick').split(','))
            while '' in isonick:
                isonick.remove('')
        hash_algorithm = 'md5'
        if __general_conf.has_option(admin, 'hash_algorithm'):
            hash_algorithm = __general_conf.get(admin, 'hash_algorithm')
        add_admin(network, user, password, capability, hash_algorithm, logins,
        maxlogins, isonick, timeout=timeout, verbose=verbose, account=account)
