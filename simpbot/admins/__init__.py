# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import os
import re

from . import capab
from . import admins
from simpbot import localedata
from simpbot import envvars
from simpbot.bottools import dummy
from six.moves import configparser
from six import string_types


i18n = localedata.get()
__general_conf = configparser.ConfigParser(**envvars.cfg_kwargs)
__general_conf.read(envvars.adminspath)
regex_local = re.compile('local ([^ ]+) ([^ ]+)')
regex_global = re.compile('global ([^ ]+)')
logging = __import__('logging').getLogger('admins')


def add_admin(network, user, hash, capabs, algm='md5', logins=0, maxlogins=0,
    ison=[], conf=None, path=None, save=False, timeout=2419200, verbose=True,
    account=[]):
    admin = admins.admins(network, user, hash, algm, logins, maxlogins, ison,
        conf, path, timeout, verbose, account)
    name = str(admin)

    if name in envvars.admins:
        logging.warning(i18n['duplicate admin'] % name)
        return False
    else:
        envvars.admins[name] = admin

    if isinstance(capabs, string_types):
        capabs = capabs.split(',')
    admin_capabs = capab.gen_capab(*capabs)
    if len(admin_capabs) == 0:
        logging.warning(i18n['admin without capabs'], name)
        return False

    admin.capab.extend(admin_capabs)

    if conf is None:
        conf = __general_conf
    if path is None:
        path = envvars.adminspath

    admin.conf = conf
    admin.confpath = path

    if not conf.has_section(name):
        admin.save()
    envvars.admins[name] = admin
    logging.info(i18n['admin added'] % name)


def has_admin(network, user):
    name = '%s %s' % ('local ' + network if network else 'global', user)
    return name in envvars.admins


def get_admin(network, user):
    name = '%s %s' % ('local ' + network if network else 'global', user)
    return envvars.admins[name]


def del_admin(network, user):
    name = '%s %s' % ('local ' + network if network else 'global', user)
    if not name in envvars.admins:
        return
    admin = envvars.admins[name]
    del envvars.admins[name]
    if admin.conf is __general_conf:
        admin.conf.remove_section(name)
        admin.save()
    if admin.confpath != envvars.adminspath:
        if not os.path.exists(admin.confpath):
            return
        elif not os.path.isfile(admin.confpath):
            return
        os.remove(admin.confpath)
    logging.info(i18n['admin deleted'] % name)


def load_admins():
    options = 'password timeout maxlogins verbose capability isonick'.split()

    for admin in __general_conf.sections():
        if dummy.invalid_section(__general_conf, admin, options):
            logging.error(i18n['bad config'], admin)
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
            logging.error(i18n['bad config'], admin)
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
