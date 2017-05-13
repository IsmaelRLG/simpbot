# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)
#
# Simpcoins! inspired by buttcoins
#---------------------------------
# Database module

import simpbot
import logging
import datetime
try: from . import config
except:     import config  # lint:ok
from peewee import SqliteDatabase, Model, CharField, DateTimeField, Check
from peewee import IntegerField, TextField, BooleanField, ForeignKeyField

peewee_logger = logging.getLogger('peewee')
peewee_logger.setLevel(logging.ERROR)

db = SqliteDatabase(simpbot.envvars.data.join('simpcoins.db'))


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = CharField(primary_key=True)  # lint:ok
    username = CharField()
    network = CharField()
    locked = BooleanField(default=False)
    manager = BooleanField(default=False)  # Manager of Simp Bank
    lines = IntegerField(default=1)
    coins = IntegerField(default=config.default_coins)
    decrease = BooleanField()
    c_block = TextField(default='')  # current block
    levelup = IntegerField(default=config.init_level)  # lines needed to level up
    chances = IntegerField(default=config.default_chances)
    last_seen = DateTimeField(default=datetime.datetime.now)
    backpack_size = IntegerField(default=config.default_bp_size)
    join_date = DateTimeField(default=datetime.datetime.now)


class Dealings(BaseModel):
    id = CharField(primary_key=True)  # lint:ok
    from_user = ForeignKeyField(User, related_name='dealings')
    to_user = ForeignKeyField(User, related_name='incomes')
    amount = IntegerField()
    date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        order_by = ('-date',)
        indexes = ((('id', 'from_user', 'to_user'), False),)


# Store zone
################################################################################
class Store(BaseModel):
    item_id = CharField(primary_key=True)
    item_name = CharField()
    sale_type = CharField()  # sale | auction
    price = IntegerField(null=True, constraints=[Check('price > 0')])  # null: Free
    description = CharField()
    category = CharField()  # category of the item
    expiration_date = DateTimeField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    status = IntegerField(default=1)  # Status of the item
                                      # 0: disabled
                                      # 1: enabled (by default)
                                      # 2: expired
                                      # 3: depleted

    added_by = ForeignKeyField(User, null=True, related_name='items_added')
    in_stock = IntegerField(null=True)  # null: unlimit items
    article_action = TextField()
    limit_uses = IntegerField(null=True)  # null: unlimit uses


class Inventary(BaseModel):
    user = ForeignKeyField(User, related_name='backpack')
    item = ForeignKeyField(Store, related_name='bought_by')
    times_uses = IntegerField(null=True)

db.connect()
db.create_tables([User, Dealings, Store, Inventary], True)