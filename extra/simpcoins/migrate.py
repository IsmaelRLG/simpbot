# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)
#
# Simpcoins! inspired by buttcoins
#---------------------------------
# dummy migration module...
from __future__ import unicode_literals

import simpbot, logging
import database as new_model
import config

import hashlib
from peewee import SqliteDatabase, Model, CharField, DateTimeField
from peewee import IntegerField, TextField, BooleanField, IntegrityError

peewee_logger = logging.getLogger('peewee')
peewee_logger.setLevel(logging.ERROR)

db = SqliteDatabase(simpbot.envvars.data.join('simpcoins-old.db'))


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

def genid(usr):
    user = (config.bot_account if usr.username == 'bot account' else usr.username)
    return hashlib.md5('%s %s' % (user.lower(), usr.network.lower())).hexdigest(), user


def move_account(usr):
    try:
        code, username = genid(usr)
        print('Migrando usuario (%s): %s | %s' % (usr.network, username, code))
        new_model.User.create(
            id=code,
            username=username,
            network=usr.network,
            locked=False,
            manager=False,
            lines=usr.lines,
            coins=usr.coins,
            decrease=usr.decrease,
            c_block=usr.c_block,
            levelup=usr.levelup,
            chances=usr.chances)
    except IntegrityError:
        print('Migración fallida...')


def move_dealing(deal):
    print('Migrando transacción: ' + deal.id)
    f = User.get(User.id == deal.sender)
    t = User.get(User.id == deal.receiver)
    try:
        new_model.Dealings.create(
            id=deal.id,
            from_user=new_model.User.get(new_model.User.id == genid(f)[0]),
            to_user=new_model.User.get(new_model.User.id == genid(t)[0]),
            amount=deal.amount,
            date=deal.date)
    except IntegrityError:
        pass


def migrate_u():
    try: users = list(User.select())
    except User.DoesNotExist: return
    for usr in users:
        move_account(usr)


def migrate_d():
    try: deals = list(Dealings.select())
    except Dealings.DoesNotExist: return
    for deal in deals:
        move_dealing(deal)


if __name__ == '__main__':
    migrate_u()
    migrate_d()
    print('Migración completada!')
