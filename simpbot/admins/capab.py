# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

template = {
    'global': ['root'],
    'local': ['admin'],

    'root': ['shutdown', 'restart', 'modules', 'over-restriction', 'api',
        'over-restriction:deny global', 'control_module', 'verbose-root',
        'control_global', 'commands', 'manager-admin', 'admin', 'superuser'],

    'admin': ['over-restriction', 'verbose', 'semi-admin', 'advance',
        'over-restriction:lock user', 'sessions', 'verbose-admin'],

    'semi-admin': ['lock user', 'unlock user', 'force:drop user', 'force:flags',
        'helper'],

    'over-restriction': [
        'over-restriction:deny command',
        'over-restriction:deny module'],
    'manager-admin': ['add local admin', 'del local admin', 'edit admin capab',
        'edit admin params', 'update admin password', 'admin-list'],

    'commands': ['control_commands', 'remove_commands'],
    'helper': ['requests', 'join', 'part', 'simple', 'update password'],
    'verbose-helper': ['verbose:new channel', 'verbose:new user',
        'verbose:drop channel', 'verbose:drop user', 'verbose:change flags', ],
    'verbose-admin': ['verbose:error', 'verbose-helper'],
    'verbose-root': ['verbose-admin', 'verbose:fail login', 'verbose:login',
        'verbose:fail use', 'verbose:control command', 'verbose:connected',
        'verbose:modules', 'verbose:update password', 'verbose:logout']
}


def gen_capab(*args, **kwargs):
    if 'ls' in kwargs:
        capabs = kwargs['ls']
    else:
        capabs = []

    def add(capab):
        if not capab in capabs and capab != '':
            capabs.append(capab)
    for capab in args:
        if capab in template:
            for sub_capab in template[capab]:
                if sub_capab in template:
                    gen_capab(sub_capab, ls=capabs)
                elif not sub_capab in capabs:
                    add(sub_capab)
        elif not capab in capabs:
            add(capab)
    return capabs
