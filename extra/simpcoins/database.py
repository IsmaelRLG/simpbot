# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)
#
# Simpcoins! inspired by buttcoins
#---------------------------------
# Database module

import simpbot
import logging
from peewee import SqliteDatabase, Model, CharField, DateTimeField
from peewee import IntegerField, TextField, BooleanField

peewee_logger = logging.getLogger('peewee')
peewee_logger.setLevel(logging.ERROR)

db = SqliteDatabase(simpbot.envvars.data.join('simpcoins.db'))


class User(Model):
    id = CharField(primary_key=True)  # lint:ok
    username = CharField()
    network = CharField()
    lines = IntegerField()
    coins = IntegerField()
    decrease = BooleanField()
    c_block = TextField()  # current block
    levelup = IntegerField()  # lines needed to level up
    chances = IntegerField()

    class Meta:
        database = db


class Dealings(Model):
    id = CharField(primary_key=True)  # lint:ok
    receiver = CharField()
    sender = CharField()
    amount = IntegerField()
    date = DateTimeField()

    class Meta:
        database = db


db.connect()
db.create_tables([User, Dealings], True)