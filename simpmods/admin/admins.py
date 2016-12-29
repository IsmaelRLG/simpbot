# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot
import random
import time
from simpbot import admins
from simpbot.bottools.irc import color
module = simpbot.get_module(sys=True)
loader = module.loader()
minlen = 4


def censore(text, per=50, sub='*'):
    text = [l for l in text]
    sublen = len(text) * float(per) / 100
    if not sublen.is_integer():
        sublen += 1
    subrang = range(len(text))
    while sublen > 0:
        sublen -= 1
        index = random.choice(subrang)
        subrang.remove(index)
        text.insert(index, sub)
        text.pop(index + 1)
    return ''.join(text)


def checkpass(admin, password):
    if len(password) <= minlen or admin.checkpass(password):
        return False

    alpha = False
    digit = False
    space = False
    charsp = False
    for ch in password:
        if ch.isalpha() and not alpha:
            alpha = True
        elif ch.isdigit() and not digit:
            digit = True
        elif ch.isspace() and not space:
            space = True
        elif not ch.isalnum() and not charsp:
            charsp = True
    return alpha and digit and not space and charsp


@loader('auth', 'auth !{account} !{password}',
    syntax="auth <cuenta> <contraseña>", need=[
    'requires nickserv',
    'registered user',
    'only:private'])
def auth(irc, ev, result, target, channel, _):
    """Identifica a un usuario como administrador de SimpBot."""
    user = irc.dbstore.get_user(_['user'].account)
    account = _['account']
    password = _['password']
    errormsg = 'Usuario ó contraseña inválida.'
    verbosemsg = color('Cuenta NickServ', 'b') + ': {user.account}, '
    verbosemsg += color('hostmask', 'b') + ': {user.mask}, '
    verbosemsg += color('Cuenta Administrador', 'b') + ': {account}'

    def fail_login(extreason='', passwd=True):
        irc.error(target, errormsg)
        if passwd:
            _['password'] = censore(password)
        else:
            _['password'] = '****'
        irc.verbose('fail login', 'Logueo fallido: ' + _(verbosemsg + ', ' +
        color('Contraseña', 'b') + ': {password}') + (
        ', ' + extreason if extreason else extreason))
        # Colocar aquí el baneo

    if admins.has_admin(None, account):
        admin = admins.get_admin(None, account)
    elif admins.has_admin(irc.servname, account):
        admin = admins.get_admin(irc.servname, account)
    else:
        return fail_login()

    if not admin.checkpass(password):
        return fail_login()
    elif len(admin.account) > 0 and not user.username in admin.account:
        return fail_login('cuenta NickServ no admitida', passwd=False)
    elif admin.has_maxlogin():
        return fail_login('maximo de logueos alcanzado', passwd=False)

    if user.isadmin() and user.admin.logins > 0:
        user.admin.logins -= 1

    user.set_admin(str(admin), time.time())
    irc.dbstore.save()
    irc.notice(target, 'Autenticado correctamente.')
    irc.verbose('login', 'Administrador autenticado: ' + _(verbosemsg))


@loader('passwd', 'passwd !{old_passwd} !{new_passwd}+',
    syntax="passwd <contraseña antigua> <contraseña nueva>", need=[
    'requires nickserv',
    'registered user',
    'admin:update password',
    'only:private'])
def update_passwd(irc, ev, result, target, channel, _):
    """Actualiza la contraseña de administrador"""
    admin = irc.dbstore.get_user(_['user'].account).admin
    old_passwd = _['old_passwd']
    new_passwd = _['new_passwd']
    errmsg = 'La antigua contraseña o la nueva contraseña es inválida. Se recu'
    errmsg += 'erda que la nueva contraseña debe ser '
    errmsg += color('mayor a ' + str(minlen), 'b')
    errmsg += ' carácteres, ésta a su vez debe contener números, letras y al me'
    errmsg += 'nos un carácter especial (como por ejemplo: ! $ & / % . - < > +)'
    errmsg += ', y no puede contener espacios en blanco.'

    if not admin.checkpass(old_passwd) or not checkpass(admin, new_passwd):
        return irc.error(target, errmsg)

    admin.update_password(new_passwd)

    msg = 'actualizó la contraseña para "%s"' % color(str(admin), 'b')
    irc.notice(target, 'Se ' + msg + ' cómo: ' + color(new_passwd, 'b'))
    irc.verbose('update password', _('{user.mask} ({user.account}) ') + msg)


@loader('forcepasswd', 'forcepasswd !{admin} !{new_passwd}',
    syntax="passwd <cuenta administrador> <contraseña nueva>", need=[
    'requires nickserv',
    'registered user',
    'admin:update admin password',
    'only:private'])
def forcepasswd(irc, ev, result, target, channel, _):
    """Fuerza el cambio de la contraseña de un administrador"""
    account = _['admin']
    new_passwd = _['new_passwd']

    if admins.has_admin(None, account):
        admin = admins.get_admin(None, account)
    elif admins.has_admin(irc.servname, account):
        admin = admins.get_admin(irc.servname, account)
    else:
        return irc.notice(target, _('Cuenta adminstrador "{admin}" inválida.'))

    if not checkpass(new_passwd):
        return irc.error(target, 'La contraseña es inválida. Se recuerda que la'
        ' nueva contraseña debe ser' + color('mayor a ' + str(minlen), 'b') +
        'carácteres, ésta a su vez debe contener números, letras y al menos un'
        'carácter especial (como por ejemplo: ! $ & / % . - < > +), y no puede'
        ' contener espacios en blanco.')

    admin.update_password(new_passwd)
    msg = 'actualizó la contraseña para "%s"' % color(str(admin), 'b')
    irc.notice(target, 'Se ' + msg + ' cómo: ' + color(new_passwd, 'b'))
    irc.verbose('update password', _('{user.mask} ({user.account}) ') + msg)


@loader('logout', 'logout', syntax="logout", need=[
    'requires nickserv', 'registered user', 'admin'])
def logout(irc, ev, result, target, channel, _):
    """Cierra la sesión de administrador."""
    user = irc.dbstore.get_user(_['user'].account)
    user.set_admin(None, None)
    irc.notice(target, 'Se ha finalizado la sesión de administrador.')
    irc.verbose(target, _('{user.mask} ({user.account})') +
    ' finalizó su sesión de administrador.')


@loader('forcelogout', 'forcelogout !{account}',
    syntax="forcelogout <cuenta simpbot>", need=[
    'requires nickserv',
    'registered user',
    'admin:forcelogout',
    'registered user:account'])
def forcelogout(irc, ev, result, target, channel, _):
    """Fuerza el cierre de la sesión de un administrador."""
    user = irc.dbstore.get_user(_['account'])
    user.set_admin(None, None)
    irc.notice(target, _('Se finalizó la sesión de administrador de {account}'))
    irc.verbose(target, _('{user.mask} ({user.account}) finalizó la sesión de '
    'administrador de ' + color(_['account'], 'b')))


@loader('sessions', 'sessions', syntax="sessions", need=[
    'requires nickserv',
    'registered user',
    'admin:sessions',
    'only:private'])
def sessions(irc, ev, result, target, channel, _):
    """Lista todas las sesiones de administradores del bot."""
    online = color('\356\210\246', 3) + ' - logged'
    offline = color('\356\210\246', 15) + ' - offline'
    for admin in simpbot.envvars.admins.values():
        if not admin.isglobal() and admin.network != irc.servname:
            continue
        if admin.logged():
            irc.notice(target, color(admin.user, 'b') + ' - ' + online)
            msg = '   |-> Red: {network}, Cuenta NickServ: {ns}, Desde: {since}'
            dateform = '[{date.tm_year}/{date.tm_mon}/{date.tm_mday}]'
            dateform += '({date.tm_hour}:{date.tm_min}:{date.tm_sec})'
            for user in irc.dbstore.admins_list():
                if not user.isadmin() or str(user.admin) != str(admin):
                    continue

                _['network'] = user.network
                _['ns'] = user.username

                _['date'] = time.localtime(user.logindate)
                _['since'] = _(dateform)
                if admin.timeout:
                    _['date'] = time.localtime(user.logindate + admin.timeout)
                    _['expire'] = _(dateform)
                    message = msg + ', Expira: {expire}'
                else:
                    message = msg
                irc.notice(target, _(message))
        else:
            irc.notice(target, color(admin.user, 'b') + ' - ' + offline)


@loader('admin', 'admin (?P<switch> add !{addacc} !{network} !{algth} !{hash}'
    ' !{capab}+|del !{delacc}|edit (?P<edit>algth|capab|level) !{value})',
    need=[
        'requires nickserv',
        'registered user',
        'admin:admin',
        'only:private'],
    help="""
Este comando permite agregar, editar ó eliminar administradores del bot.
Si desea agregar un administrador deberá seguir la siguiente sintaxis:
\2Sintaxis\2: admin add <cuenta> <red> <algoritmo hash> <hash> <capacidades>
Argumentos:
    cuenta -- Nombre de la cuenta de administrador
    red -- Nombre de la red a la que pertenecerá el administrador, si se desea
        crear una cuenta que se use en todas las redes, se deberá usar como
        parámetro \2*\2
    Algoritmo HASH -- Nombre de la función HASH a utilizar. Los algoritmos
        disponibles son: SHA, SHA1, SHA224, SHA256, SHA384, SHA512,
        MD4, MD5, DSA, RIPEMD160, whirlpool. Se recomienda utilizar \2MD5\2.
    hash -- Clave de administrador cifrada con la función hash
    """)
def admin(irc, ev, result, target, channel, _):
    pass