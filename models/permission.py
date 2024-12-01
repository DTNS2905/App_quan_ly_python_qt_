from PyQt6 import QtSql

from common.model import SqliteModel
from configs import DATABASE_NAME
from sql_statements.permission import ADD_PERMISSION_SQL, \
    PERMISSION_USER_VIEW_SQL, CREATE_PERMISSION_TABLE_SQL, CREATE_PERMISSION_USER_TABLE_SQL, \
    GET_PERMISSION_BY_USERNAME_SQL, ASSIGN_PERMISSION_BY_USERNAME_SQL


class PermissionModel(SqliteModel):
    _junction_table_sql = CREATE_PERMISSION_USER_TABLE_SQL
    _add_permission_sql = ADD_PERMISSION_SQL
    _assign_permission_sql = ASSIGN_PERMISSION_BY_USERNAME_SQL
    _get_permission_by_username = GET_PERMISSION_BY_USERNAME_SQL
    _fetch_user_permission_sql = PERMISSION_USER_VIEW_SQL

    def __init__(self, database_name=DATABASE_NAME, table_create_sql=CREATE_PERMISSION_TABLE_SQL):
        super().__init__(database_name, table_create_sql)
        self.init_junction_table()

    def init_junction_table(self):
        # Create the junction table
        junction_query = QtSql.QSqlQuery()
        if not junction_query.exec(self._junction_table_sql):
            raise Exception(f"Failed to create junction table: {junction_query.lastError().text()}")

    def assign_permission_to_user(self, username, permission):
        """Link a user to a permission in the junction table."""
        query = QtSql.QSqlQuery()
        query.prepare(self._assign_permission_sql)
        query.addBindValue(username)
        query.addBindValue(permission)
        if not query.exec():
            print(f"Error assigning permission: {query.lastError().text()}")
            raise Exception(f"Error assigning permission: {query.lastError().text()}")

    def get_permission_by_username(self, username: str):
        """Verify if a user has a specific permission."""
        query = QtSql.QSqlQuery()
        query.prepare(self._get_permission_by_username)
        query.addBindValue(username)
        results = []
        while query.next():
            permission = query.value(0)  # Permission
            results.append(permission)

        return results

    def fetch_user_permissions(self):
        """Fetch all usernames and their permissions."""
        query = QtSql.QSqlQuery()
        query.prepare(self._fetch_user_permission_sql)
        results = []
        while query.next():
            username = query.value(0)  # Username
            permission = query.value(1)  # Permission
            results.append((username, permission))

        return results

    def add_permission(self, permission):
        """Add a single permission to the database."""
        query = QtSql.QSqlQuery()
        query.prepare(self._add_permission_sql)
        query.addBindValue(permission)
        if not query.exec():
            raise Exception(f"Error adding permission '{permission}': {query.lastError().text()}")
