# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import httplib2
import json

from six.moves import urllib
from . import config


class request:

    def __init__(self, host, port, network, username, password):
        self.host = host
        self.port = port
        self.network = network
        self.http = httplib2.Http()
        self.username = username
        self.password = password

    def basejoin(self, url):
        return urllib.parse.urljoin(self.get_url(), url)

    def get_url(self):
        return "http://%s:%s" % (self.host, self.port)

    def request(self, url, method, data):
        return self.http.request(
            self.basejoin(url),
            method.upper(),
            json.dumps(data),
            headers={'Content-Type': "application/json"})

    def post(self, url, extra={}):
        return self.request(url, 'POST', self.basedata(extra))

    def get(self, url, extra={}):
        return self.request(url, 'POST', self.basedata(extra))

    def basedata(self, extra={}):
        data = {
            'username': self.username,
            'password': self.password,
            'network': self.network}
        data.update(extra)

    def connections(self):
        return self.get(config.URL_CONNECTIONS)

    def reconfigure(self):
        return self.post(config.URL_RECONFIGURE)

    def connect(self, servername):
        return self.post(config.URL_CONNECT, {'network': servername})

    def reconnect(self, servername):
        return self.port(config.URL_RECONNECT, {'network': servername})

    def disconnect(self, servername):
        return self.post(config.URL_DISCONNECT, {'network': servername})

    def command(self, query):
        return self.post(config.URL_COMMANDS, {'action': query})