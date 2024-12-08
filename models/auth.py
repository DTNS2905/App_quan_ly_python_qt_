import logging

from PyQt6 import QtSql

from common.auth import hash_password
from common.model import SqliteModel
from configs import DATABASE_NAME
from sql_statements.auth import CREATE_USER_TABLE_SQL, INSERT_USER_SQL, VERIFY_USER_SQL


class AuthModel(SqliteModel):
    _password_encrypt = hash_password
    _user_insert_sql = INSERT_USER_SQL
    _user_verify_sql = VERIFY_USER_SQL

    def __init__(
        self, database_name=DATABASE_NAME, table_create_sql=CREATE_USER_TABLE_SQL
    ):
        super().__init__(database_name, table_create_sql)

    def add_user(self, username, password, is_superuser=False):
        hashed_password = hash_password(password)
        query = QtSql.QSqlQuery()
        query.prepare(self._user_insert_sql)
        query.addBindValue(username)
        query.addBindValue(hashed_password)
        query.addBindValue(is_superuser)
        if not query.exec():
            logging.error(f"Error adding user: {query.lastError().text()}")

    def create_superuser(self, username, password):
        # Check if the user already exists
        if self.verify_user(username):
            logging.info(f"Superuser '{username}' already exists.")
        else:
            self.add_user(username, password, is_superuser=True)
            logging.info(f"Superuser '{username}' created successfully!")

    def verify_user(self, username):
        query = QtSql.QSqlQuery()
        query.prepare(self._user_verify_sql)
        query.addBindValue(username)
        if query.exec() and query.next():
            return query.value(0)
        return None
