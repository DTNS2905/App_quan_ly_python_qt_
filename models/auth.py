from PyQt5 import QtSql

from common.auth import hash_password
from common.model import SqliteModel
from configs import DATABASE_NAME
from sql_statements.auth import CREATE_USER_TABLE_SQL, INSERT_USER_SQL, VERIFY_USER_SQL


class AuthModel(SqliteModel):
    _password_encrypt = hash_password
    _user_insert_sql = INSERT_USER_SQL
    _user_verify_sql = VERIFY_USER_SQL

    def __init__(self, database_name=DATABASE_NAME, table_create_sql=CREATE_USER_TABLE_SQL):
        super().__init__(database_name, table_create_sql)

    def add_user(self, username, password):
        hashed_password = self._password_encrypt(password)
        query = QtSql.QSqlQuery()
        query.prepare(self._user_insert_sql)
        query.addBindValue(username)
        query.addBindValue(hashed_password)
        if not query.exec_():
            print(f"Error adding user: {query.lastError().text()}")

    def verify_user(self, username):
        query = QtSql.QSqlQuery()
        query.prepare(self._user_verify_sql)
        query.addBindValue(username)
        if query.exec_() and query.next():
            return query.value(0)
        return None
