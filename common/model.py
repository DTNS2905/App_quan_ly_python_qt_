import abc

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


