# -*- coding: utf-8 -*-
# Simple Bot (SimpBot)
# Copyright 2016-2017, Ismael Lugo (kwargs)

from .models import db_base
from .models import DatabaseError
from playhouse.migrate import SqliteMigrator, PostgresqlMigrator, MySQLMigrator


class DatabaseMigrator(models.db_base):
    @classmethod
    def migrate(self, version, version_history, migrator):
        if version not in version_history:
            DatabaseError('Unknown version {version}, ')
    def __init__(self, *args, **kwargs):

    def migrate(self, version):



def migrator_v1_1(migrator):
    pass

schemas = {
    0.1: migrator_v1_1
}
