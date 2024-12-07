import abc
import logging
import sqlite3

from PyQt6 import QtSql


class Model(abc.ABC):

    @abc.abstractmethod
    def init_db(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def close_connection(self):
        raise NotImplementedError()


class SqliteModel(Model):
    def __init__(self, database_name, table_create_sql):
        self.db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(database_name)
        if not self.db.open():
            raise Exception(f"Database error: {self.db.lastError().text()}")

        self._table_create_sql = table_create_sql
        self.init_db()

    def init_db(self):
        query = QtSql.QSqlQuery()
        query.exec(self._table_create_sql)

    def close_connection(self):
        self.db.close()
        QtSql.QSqlDatabase.removeDatabase("QSQLITE")


class NativeSqlite3Model(Model):
    def __init__(self, database_name, table_create_sql):
        self.connection = sqlite3.connect(database_name)
        self._table_create_sql = table_create_sql
        self.init_db()

    def init_db(self):
        cur = self.connection.cursor()
        try:
            cur.execute(self._table_create_sql)
            self.connection.commit()
            logging.info(f"Table created successfully:\n{self._table_create_sql}")
        except sqlite3.Error as error:
            logging.error(f"Error creating table: {error}")
        finally:
            cur.close()

    def close_connection(self):
        self.connection.close()
