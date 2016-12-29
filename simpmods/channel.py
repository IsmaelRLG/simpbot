# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import simpbot
from simpbot import mode
from simpbot.bottools.irc import color
from simpbot.bottools.irc import valid_mask
module = simpbot.get_module(sys=True)
loader = module.loader()


@loader('register channel', 'register channel !{chan_name}',
    syntax="register channel <canal>", need=[
    'requires nickserv',
    'registered user',
    'unregistered chan:chan_name'])
def register(irc, ev, result, target, channel, _):
    """Registra algún canal en el bot."""
    channel = _['chan_name']
    user = _['user']

    def check_max():
        ok = True
        no = False
        if irc.dbstore.max_channels == 0:
            return ok
        total = len(irc.dbstore.store_request['chan'])
        total += irc.dbstore.total_chan()
        error = 'Se alcanzó el límite de canales para solicitud ó registro.'
        if total < irc.dbstore.max_channels:
            return ok
        elif (total + 1) == irc.dbstore.max_channels:
            irc.verbose('request', 'NOTIFICACIÓN: ' + error)
        irc.error(target, error)
        return no

    if irc.dbstore.chanregister == 'allow':
        if not check_max():
            return
        irc.dbstore.register_chan(channel)
        channel = irc.dbstore.get_chan(channel)
        channel.set_flags(irc.dbstore.get_user(user.account), 'founder')
        irc.dbstore.save()
        msg = 'Se registró el canal "{chan_name}" a la cuenta "{user.account}".'
        msg = _(msg)

        irc.verbose('new channel', msg)
        irc.notice(target, msg)
        irc.join(channel)
    elif irc.dbstore.chanregister == 'request':
        if irc.dbstore.has_request('chan', (channel, user.account)):
            request = irc.dbstore.get_request('chan', channel)
            if request[1] == user.account.lower():
                irc.error(target, 'Ya tiene una solicitud abierta.')
                return
            _['usr'] = request[1]
            msg = 'No se pudo solicitar el registro del canal "{chan_name}", '
            msg += 'debido a que ya existe una solicitud de registro por parte '
            msg += 'de la cuenta "{user.account}".'
            irc.error(target, _(msg))
            return

        if not check_max():
            return
        irc.dbstore.request('chan', (channel, user.account))
        msg = '{user.nick} ({user.user@user.host}), cuenta: "{user.account}"'
        msg += 'solicita aprobación del canal "{chan_name}", código de '
        msg += 'aprobación: "%s".'
        msg = msg % color(irc.dbstore.get_request(channel)[0], 'b')
        irc.verbose('request', _(msg))
        irc.notice(target, _('Solicitud del canal "{chan_name}" enviada.'))
    elif irc.dbstore.chanregister == 'deny':
        irc.error(target, 'Se encuentra inhabilitado el registro de canales.')


@loader('drop channel', 'drop channel !{chan_name}',
    syntax="drop channel <#canal>",
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:chan_name',
        'flags:F'
    ])
def drop(irc, ev, result, target, channel, _):
    """Elimina algún canal del bot."""
    user = _['user']
    msg = 'Para evitar el uso accidental de este comando, esta operación tiene '
    msg += 'que ser confirmada. Por favor confirme respondiendo con /'
    msg += color('msg {irc.nickname} confirm drop:chan {chan_name} {h}', 'b')
    if irc.dbstore.has_drop('chan', _['chan_name']):
        _['h'] = irc.dbstore.get_hashdrop(_['chan_name'])
    else:
        _['h'] = irc.dbstore.drop('chan', _['chan_name'])
    irc.notice(user.nick, _(msg))


@loader('confirm drop:chan', 'confirm drop:chan !{chan_name} !{code}',
    syntax="confirm drop:chan <#canal> <código>", need=[
    'requires nickserv',
    'registered user',
    'registered chan:chan_name',
    'flags:F'])
def confirm(irc, ev, result, target, channel, _):
    """Confirma la eliminación de un canal en el bot."""
    user = _['user']
    code = _['code']
    chan = _['chan_name']
    if len(code) != 32 or not irc.dbstore.has_drop('chan', chan) or \
    irc.dbstore.get_hashdrop(_['chan_name']) != code:
        irc.error(user.nick, 'Código de confirmación inválido.')
        return
    irc.dbstore.del_drop('chan', chan)
    irc.dbstore.drop_chan(chan)
    msg = _('Canal "{chan_name}" eliminado')
    irc.notice(user.nick, msg + '.')
    irc.verbose('drop channel', msg + _(' por "{user.account}".'))


@loader('flags',
    regex='flags !{chan_name} (?P<fg_type>list|!{target} !{flags})',
    syntax="flags <#canal> (list | [mask | cuenta] [+/- | plantilla])",
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:chan_name',
        'flags:f'
    ],

    help="""
El comando FLAGS permite otorgar ó eliminar privilegios en un nivel más
específico, no generalizado. Éste admite masks y cuentas de usuario.

Los flags pueden modificarse usando + para otorgar y - para eliminar
privilegios; también modificarse indicando el nombre de la plantilla, para
obtener más información sobre las plantillas, envíe lo siguiente:
/msg {irc.nickname} help template

Si usted es un fundador, y desea otorgar / remover privilegios de fundador
a un segundo ó a usted mismo debera usar el comando FOUNDER, para obtener
más información sobre este comando envie lo siguiente:
    /msg {irc.nickname} help founder
No se pueden conceder privilegios de fundador otorgando +F, igualmente no está
permitido conceder los siguientes privilegios a un mask: +Ffs.

Lista de privilegios:
    +v - Habilita el uso del comando voice
    +V - Habilita el uso del comando devoice
    +o - Habilita el uso del comando op
    +O - Habilita el uso del comando deop
    +b - Habilita el uso del comando ban
    +B - Habilita el uso del comando unban
    +i - Habilita el uso del comando invite
    +k - Habilita el uso del comando kick
    +r - Habilita el uso del comando remove
    +l - Permite ver la lista de flags
    +t - Habilita el uso del comando topic
    +m - Habilita el uso del comando mode
    +s - Permite cambiar las plantillas
    +f - Concede privilegios de administrador
    +F - Concede privilegios de fundador

Ejemplos:
    /msg {irc.nickname} FLAGS #foo foouser OP
    /msg {irc.nickname} FLAGS #foo foouser +Vbiklmotv
    /msg {irc.nickname} FLAGS #foo *!*@hostname +Vbiklmotv
    /msg {irc.nickname} FLAGS #foo nick!*@host OP
""")
def flags(irc, ev, result, target, channel, _):
    channel = irc.dbstore.get_chan(_['chan_name'])
    account = _['target']
    user = _['user']

    if _['fg_type'] == 'list':
        n = 0
        parsename = '% -' + str(irc.features.nicklen) + 's'
        irc.notice(target, _('Lista de FLAGS para \2{chan_name}\2.'))
        irc.notice(target, '    ' + parsename % 'Nombre' + '  Flags')
        irc.notice(target, '--- ' + '-' * irc.features.nicklen + '  -----')
        for name, flags_ls in channel.flags.items():
            n += 1
            if hasattr(name, 'username'):
                name = name.username
            elif isinstance(name, tuple):
                name = name[1]
            _['name'] = parsename % name
            _['flags'] = flags_ls
            _['n'] = str(n).zfill(3)
            irc.notice(target, _('{n} {name} +{flags}'))
        else:
            if n == 0:
                return
        irc.notice(target, '--- ' + '-' * irc.features.nicklen + '  -----')
        return

    # El usuario a modificar los flags
    if not valid_mask(account):
        account = irc.dbstore.get_user(account)
        if not account:
            return irc.error(target, _('Usuario ó mask inválido: {target}'))

    # El usuario que los modifica
    account_2 = irc.dbstore.get_user(user.account)

    ddel = 'F'
    dadd = 'F'

    if hasattr(account, 'username'):
        _['target'] = account.username
        if account_2.username.lower() != account.username.lower():
            if channel.has_flags(account):
                if 'F' in channel.get_flags(account):
                    ddel += 'f'

    diff = channel.set_flags(account, _['flags'], dadd, ddel)
    irc.dbstore.save()
    if not diff:
        return irc.error(target, 'No se pudieron establecer los flags.')

    if diff[0] == diff[1]:
        irc.notice(target, _('Flags para {target} en {chan_name} sin cambios.'))
        return

    diff = list(diff)
    if diff[1] is None:
        diff[1] = '---'

    if diff[0] is None:
        diff[0] = '---'
    _['diff'] = diff
    msg = _('\2{target}\2: (\2{diff[0]}\2)  ->   (\2{diff[1]}\2)')
    irc.notice(target, 'Se modificaron los flags para ' + msg)
    if target.lower() != channel.channel and channel.verbose:
        msg = _('{user.nick} ({user.account}) modificó los flags ') + msg
        irc.notice(target, msg)


@loader('founder', 'founder !{chan_name} (?P<switch>add|del) !{account}',
    syntax="founder <#canal> [add | del] <cuenta>",
    need=[
        'requires nickserv',
        'registered user',
        'registered user:account',
        'registered chan:chan_name',
        'flags:F'],
    help="""
Este comando permite conceder ó eliminar privilegios de fundador a un usuario,
no se admite el uso de masks para establecer fundadores, sólo está permitido
usar cuentas de usuario registrados en el bot.

Para conceder este privilegio deberá usarse \2add\2, en caso contrario, de
querer remover el privilegio de fundador debe usarse \2del\2.
""")
def founder(irc, ev, result, target, channel, _):
    channel = irc.dbstore.get_chan(_['chan_name'])
    account = irc.dbstore.get_user(_['account'])
    switch = _['switch']
    if switch == 'add':
        diff = channel.set_flags(account, '+F')
    elif switch == 'del':
        diff = channel.set_flags(account, '-F')

    if not diff or diff[0] == diff[1]:
        return irc.error(target, 'No se pudo modificar los fundadores.')

    irc.dbstore.save()
    diff = list(diff)
    if diff[1] is None:
        diff[1] = '---'

    if diff[0] is None:
        diff[0] = '---'
    _['diff'] = diff
    msg = _('\2{account}\2: (\2{diff[0]}\2)  ->   (\2{diff[1]}\2)')
    irc.notice(target, 'Se modificaron los flags para ' + msg)
    if target.lower() != channel.channel and channel.verbose:
        msg = _('{user.nick} ({user.account}) modificó los flags ') + msg
        irc.notice(target, msg)


@loader('template', 'template !{chan_name} (list|!{template} !{flags})',
    syntax="template <#canal> [list | <plantilla> <flags>]",
    need=[
        'requires nickserv',
        'registered user',
        'registered chan:chan_name',
        'flags:s'],
    help="""
El comando TEMPLATE permite la definición de conjuntos de flags, ésto para
simplificar el uso del comando FLAGS.

Por defecto se incluyen las siguientes plantillas:
    PLANTILLA  FLAGS
    ---------  ------------ ----------------------------
    FOUNDER    +FOVbfiklmorstv
    ADMIN      +OVbfiklmorstv
    OP         +Vbiklmotv
    VOICE      +Viltv
    CLEAR      \2Plantilla especial\2: Quita todos los flags
    ---------  -----------------------------------------

Para mostrar la lista de plantillas de algún canal, sólo debe indicarse como
único parametro "\2list\2".
Sintaxis: template <#canal> list

De añadir un segundo argumento, se modifica la plantilla. La modificación debe
comenzar con + (para añadir) ó - (para eliminar). Sálo se podrán añadir los
privilegios mencionados en FLAGS; para más información sobre los privilegios:
    /msg {irc.nickname} help flags

En caso que la plantilla le sean eliminado todos los flags y quede vacia, la
plantilla como consecuencia es eliminada.
""")
def template(irc, ev, result, target, channel, _):
    channel = irc.dbstore.get_chan(_['chan_name'])
    template_name = _['template'].lower()
    if template_name == '' and _['flags'] == '':
        n = 0
        irc.notice(target, _('Lista de plantillas para \2{chan_name}\2.'))
        irc.notice(target, '    Nombre               Flags')
        irc.notice(target, '--- -------------------  -----')
        for template, flags_ls in channel.template.items():
            n += 1
            _['template'] = '% -21s' % template
            _['flags'] = flags_ls
            _['n'] = str(n).zfill(3)
            irc.notice(target, _('{n} {template} +{flags}'))
        else:
            if n == 0:
                return
        return irc.notice(target, '--- -------------------  -----')

    if len(template_name) > 19:
        return irc.error(target, 'Nombre de plantilla muy largo.')

    if not template_name in channel.template:
        channel.template[template_name] = ''

    for sign, ch, null in mode._parse_modes(_['flags'], only='FOVbfiklmorstv'):
        value = channel.template[template_name]
        if sign == '+':
            if ch in value:
                continue
            value += ch
        elif sign == '-':
            if not ch in value:
                continue
            value = value.replace(ch, '')
        channel.template[template_name] = value

    value = [n for n in channel.template[template_name]]
    value.sort()
    value = ''.join(value)
    channel.template[template_name] = value

    if len(channel.template[template_name]) == 0 and template_name != 'clear':
        del channel.template[template_name]
        irc.dbstore.save()
        irc.notice(target, _('Se eliminó la plantilla: {template}.'))
    else:
        irc.dbstore.save()
        _['flags'] = channel.template[template_name]
        if len(_['flags']) == 0:
            _['flags'] = '---'
        irc.notice(target, _('Ahora la plantilla {template} contiene \2{flags}\2'))
