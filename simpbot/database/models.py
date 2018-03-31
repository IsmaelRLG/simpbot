# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

import logging
import datetime
import uuid

from six.moves import cPickle
from six import PY3
from peewee import SqliteDatabase, PostgresqlDatabase, MySQLDatabase
from peewee import Model, CharField, DateTimeField, UUIDField, FloatField
from peewee import IntegerField, TextField, BooleanField, ForeignKeyField
from . import __version__, __uuid__

logger = logging.getLogger('simpbot')
peewee_logger = logging.getLogger('peewee')
peewee_logger.setLevel(logging.ERROR)


class PickleField(TextField):
    def db_value(self, value):
        try:
            dump = cPickle.dumps(value)
        except:
            dump = cPickle.dums(None)
        return dump

    def python_value(self, value):
        return cPickle.loads(value)


class DatabaseError(Exception):
    def __init__(self, *args):
        super(DatabaseError, Exception).__init__()
        self.args = args
        self.message = args[0] if len(args) > 0 else ''

    def __str__(self):
        return ''.join(args)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, str(self))


class db_base(object):
    SQLITE_DB = 0
    MYSQL_DB = 1
    PSQL_DB = 2

    def __init__(self, db_type, **kwargs):
        self.db_type = db_type
        self.__kwargs = kwargs
        self.database = self.getDatabase()
        self.db_list = {}

#    def __getattr__(self, attr):
#        if attr in self.database:
#            return self.database[attr]
#        else:
#            return getattr(self, attr)

    def getDatabase(self):
        if self.db_type == self.SQLITE_DB or self.db_type is None:
            return SqliteDatabase(self.__kwargs['db_path'])
        elif self.db_type == self.PSQL_DB:
            return PostgresqlDatabase(**self.__kwargs)
        elif self.db_type == self.MYSQL_DB:
            if 'password' in self.__kwargs:
                self.__kwargs['passwd'] = self.__kwargs['password']
                del self.__kwargs['password']
            return MySQLDatabase(**self.__kwargs)

    def connect(self):
        try:
            self.database.connect()
        except Exception as e:
            raise DatabaseError("Can't open database connection. Error: ", str(e))

    def create_tables(self, models, safe=False):
        self.database.create_tables(models, safe)
        for model in models:
            self.db_list[model.__name__] = model

    def create_table(self, model_class, safe=False):
        self.database.create_tables(model_class, safe)
        self.db_list[model_class.__name__] = model_class

    def build_base(self):
        if 'BaseModel' in self.db_list:
            BaseModel = self.getTable('BaseModel')
        else:
            class BaseModel(Model):
                class Meta:
                    database = self.database
            self.db_list['BaseModel'] = BaseModel

        class Extras(BaseModel):
            uuid = UUIDField(primary_key=True)
            version = CharField()

        return BaseModel, Extras

    def getTable(self, table_name):
        if table_name in self.db_list:
            return self.db_list[table_name]
        else:
            raise DatabaseError("Unknown table name: ", table_name)


class builder(db_base):

    def build_models(self):
        BaseModel, Extras = self.build_base()
        models = []
        add_model = models.append

        class Config(BaseModel):
            varname = CharField(primary_key=True)
            varvalue = TextField()
            vartype = IntegerField()
            description = TextField(null=True)
            # Notes
            # ---------------------------------------------------+
            # VARIABLE                    | VALUE                |
            # ---------------------------------------------------+
            # DEFAULT_AUTH_TYPE           | NS                   |
            # DEFAULT_LANG                | SYSTEM               |
            # DEFAULT_DATE_DAY_FORMAT     | %m/%d/%Y             |
            # DEFAULT_DATE_HOUR_FORMAT    | %H:%M:%S             |
            # DEFAULT_DATE_FULL_FORMAT    | %H:%M:%S %m/%d/%Y    |
            # DEFAULT_GMT                 | SYSTEM               |
            # MAX_LOCK_HISTORY            | 10                   |
            # DB_VERSION                  | SYSTEM               |
        add_model(Config)

        # Netork
        # ----------------------------------
        class Network(BaseModel):
            uuid = UUIDField(primary_key=True, default=uuid.uuid4)
            name = CharField()
            host = CharField()
            port = IntegerField(default=6667)
            ssl = BooleanField(default=False)
            password = TextField(null=True)
            active = BooleanField(default=True)
        add_model(Network)

        class Network_Properties(BaseModel):
            network = ForeignKeyField(Network, related_name='properties')
            varname = CharField()
            varvalue = TextField()
            vartype = BooleanField()
            # VARIABLE                    | TYPE
            # ----------------------------+----------------------
            # PREFIX                      | STRING
            # NICKNAME                    | STRING
            # NS_PASSWORD                 | STRING
            # NS_USERNAME                 | STRING
            # SASL                        | BOOLEAN
        add_model(Network_Properties)

        class Admin(BaseModel):
            uuid = UUIDField(primary_key=True, default=uuid.uuid4)
            user = CharField()
            network = ForeignKeyField(Network, related_name='admins', null=True)
            full_name = TextField()
            passwd = CharField()  # hash password
            hash_algorithm = CharField()
            verbose = BooleanField()
            timeout = IntegerField()
            maxlogins = IntegerField()
            status = BooleanField(default=True)
            date = DateTimeField(default=datetime.datetime.now)
        add_model(Admin)

        # Users
        # ----------------------------------
        class User(BaseModel):
            uuid = UUIDField(primary_key=True, default=uuid.uuid4)
            network = ForeignKeyField(Network, related_name='users')
            username = CharField(null=True)
            hostname = CharField(null=True)
            nickname = CharField(null=True)
            date = DateTimeField(default=datetime.datetime.now)
        add_model(User)

        class User_Properties(BaseModel):
            account = ForeignKeyField(User, related_name='properties')
            varname = CharField()
            varvalue = TextField()
            vartype = IntegerField()
            date = DateTimeField(default=datetime.datetime.now)
            # VARIABLE                    | TYPE
            # ----------------------------+----------------------
            # DATE_DAY_FORMAT             | STRING
            # DATE_HOUR_FORMAT            | STRING
            # DATE_FULL_FORMAT            | STRING
            # LANG                        | STRING
        add_model(User_Properties)

        class User_Lock(BaseModel):
            account = ForeignKeyField(User, related_name='status')
            locked = BooleanField(default=False)
            locked_by = ForeignKeyField(Admin, related_name='user_locks')
            lock_reason = TextField(null=True)
            date = DateTimeField(default=datetime.datetime.now)
        add_model(User_Lock)

        # Channels
        # ----------------------------------
        class Channel(BaseModel):
            uuid = UUIDField(primary_key=True, default=uuid.uuid4)
            network = ForeignKeyField(Network, related_name='channels')
            name = CharField()
            date = DateTimeField(default=datetime.datetime.now)
        add_model(Channel)

        class Channel_Properties(BaseModel):
            channel = ForeignKeyField(Channel, related_name='properties')
            varname = CharField()
            varvalue = TextField()
            vartype = BooleanField()
            # VARIABLE                    | TYPE
            # ----------------------------+----------------------
            # DATE_DAY_FORMAT             | STRING
            # DATE_HOUR_FORMAT            | STRING
            # DATE_FULL_FORMAT            | STRING
            # LANG                        | STRING
        add_model(Channel_Properties)

        class Channel_Templates(BaseModel):
            channel = ForeignKeyField(Channel, related_name='templates')
            name = CharField()
            value = CharField()
            date = DateTimeField(default=datetime.datetime.now)
        add_model(Channel_Templates)

        class Channel_Flags(BaseModel):
            channel = ForeignKeyField(Channel, related_name='flags')
            account = ForeignKeyField(User, related_name='flags')
            template = ForeignKeyField(Channel_Templates, related_name='used', null=True)
            value = CharField(null=True)
            founder = BooleanField(null=True)
            successor = BooleanField(null=True)
            date = DateTimeField()
        add_model(Channel_Flags)

        class Channel_Lock(BaseModel):
            channel = ForeignKeyField(Channel, related_name='status')
            locked = BooleanField(default=True)
            locked_by = ForeignKeyField(Admin, related_name='user_locks')
            lock_reason = TextField(null=True)
            date = DateTimeField(default=datetime.datetime.now)
        add_model(Channel_Lock)

        # Admininistrator
        # ----------------------------------
        class Admin_ACL(BaseModel):
            account = ForeignKeyField(Admin, related_name='acl')
            acl = CharField()
            desc = TextField()
            date = DateTimeField(default=datetime.datetime.now)
        add_model(Admin_ACL)

        class Admin_Sessions(BaseModel):
            admin_account = ForeignKeyField(Admin, related_name='admin_sessions')
            user_account = ForeignKeyField(User, related_name='admin', null=True)
            network = ForeignKeyField(Network, related_name='admin_sessions')
            hostname = CharField()
            login_date = DateTimeField(default=datetime.datetime.now)
        add_model(Admin_Sessions)

        class Firewall(BaseModel):
            rule = CharField()
            zone = IntegerField()  # 0: user, 1: channel, 2: command, 3: module, 4: system
            type = IntegerField()  # 0: Channel, 1: User, 2: Mask
            action = IntegerField()  # 0: allow, 1: deny, 2: ignore,
            network = ForeignKeyField(Network, related_name='rules', null=True)
            owner_uuid = UUIDField()
            date = DateTimeField(default=datetime.datetime.now)
            expire_date = IntegerField(null=True)
        add_model(Firewall)

        class Scheduler(BaseModel):
            uuid = UUIDField(primary_key=True, default=uuid.uuid4)
            handlers = PickleField(null=True)
            function = PickleField()
            args = PickleField()
            kwargs = PickleField()

            status = IntegerField(default=0)
            date = DateTimeField(default=datetime.datetime.now)
            exec_in = FloatField()
            delay = FloatField()
            max_attempts = IntegerField()

            p_done = BooleanField()
            p_exec = BooleanField()
            p_thread = BooleanField()
            p_attempts = BooleanField()
            p_rerun = BooleanField(null=True)

        return models

    def build(self):
        Extras = self.build_base()[1]
        self.create_table(Extras, safe=True)
        try:
            version = Extras.get(uuid=__uuid__)
        except Extras.DoesNotExist:
            Extras.create(uuid=__uuid__, version=__version__)
        else:
            if version.version != __version__:
                raise DatabaseError('Database has changed, needs to be migrated')
        self.create_tables(self.build_models())
