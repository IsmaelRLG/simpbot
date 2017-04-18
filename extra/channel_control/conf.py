# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import simpbot
import re

cc_manager = simpbot.envvars.data.new_wa('channel-control')
groups = ['clon', 'flood', 'link', 'repeat', 'upper', 'badwords']
conf_regex = '(?P<group_name>%s) (?P<netw>[^ ]+) (?P<chan>[^ ]+) (?P<cfg>[^ ]+)'
conf_regex = re.compile(conf_regex % groups)
conf_filename = 'channel_control.txt'
wl_filename = '%s.wl'
wl_maker = lambda name: simpbot.control.control(wl_filename % name, cc_manager)

wl_clon,     clon     = wl_maker('clon'),     {}
wl_flood,    flood    = wl_maker('flood'),    {}
wl_link,     link     = wl_maker('link'),     {}
wl_repeat,   repeat   = wl_maker('repeat'),   {}
wl_upper,    upper    = wl_maker('upper'),    {}
wl_badwords, badwords = wl_maker('badwords'), {}
wl_generic,  generic  = wl_maker('generic'),  {}


def trigger_delete_channel(result, args, kwargs):
    network = args[0].name()
    channel = args[1].lower()
    for group_name in groups:
        group = eval(group_name)
        if network in group and channel in group[network]:
            del group[network][channel]
    return result
simpbot.dbstore.dbstore.add_trigger('post', 'drop_chan', trigger_delete_channel)


def read_conf():
    if not cc_manager.exists(conf_filename):
        cc_manager.open(conf_filename, 'w').close()

    for line in cc_manager.open(conf_filename, 'r'):
        if line == '' or line.isspace():
            continue

        match = conf_regex.match(line.strip())
        if match is None:
            continue
        group = match.group('group_name')
        network = match.group('netw').lower()
        channel = match.group('chan').lower()
        config = []
        for cfg in match.group('cfg').split(','):
            if cfg.isdigit():
                cfg = int(cfg)
            elif cfg.replace('-').isdigit():
                cfg = int('-' + cfg)
            elif cfg == 'True':
                cfg = True
            elif cfg == 'False':
                cfg = False
            config.append(cfg)

        if not network in group:
            group[network] = {}

        if not channel in group[network]:
            group[network][channel] = config


def save_conf():
    line_format = '{group_name} {network} {channel} {conf}'
    with cc_manager.open(conf_filename, 'w') as cfg:
        for group_name in groups:
            group = eval(group_name)
            for network in group.keys():
                for channel in group[network].keys():
                    conf = [str(conf) for conf in group[network][channel]]
                    conf = ','.join(conf)
                    cfg.write(line_format.format(**vars()))


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