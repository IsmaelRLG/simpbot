# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016, Ismael Lugo (kwargs)

import httplib, socket, urllib, json, re  # lint:ok
import simpbot


@simpbot.commands.addCommand('ip !{ipaddr}', 'Geolocaliza una ip', 'ip')
def geoip(irc, ev, result, target, channel, _):
    text = urllib.quote(_['ipaddr'])
    try:
        http = httplib.HTTPConnection("ip-api.com")
        http.request("GET", "/json/{0}?fields=65535".format(text))
        data = json.loads(http.getresponse().read().decode('utf-8'))
        if data['status'] != "success":
            raise ValueError
    except:
        irc.error(target, _('No se pudo geolocalizar "{ipaddr}"'))
        return

    resu = []
    encode = lambda s: s.encode('UTF-8') if isinstance(s, unicode) else s
    form = lambda key, val: resu.append('\2{}\2: {}'.format(key, encode(val)))
    form('IP', _['ipaddr'])
    if data['reverse'] != u"":
        resu[0] += " - {}".format(encode(data['reverse']))

    if data['country'] != u"":
        form('País', data['country'])
    if data['region'] != u"":
        form('Región', data['region'])
    if data['city'] != u"":
        form('Ciudad', data['city'])
    if data['isp'] != u"":
        form('ISP', data['isp'])
    if data['org'] != u"":
        form('Organización', data['org'])
    if data['as'] != u"":
        form('ASN', data['as'])

    if data['timezone'] != "":
        form('Zona horaria', data['org'])
        resu.append(resu.pop() + " \2\2: {0}".format(encode(data['timezone'])))
    irc.msg(target, ', '.join(resu))