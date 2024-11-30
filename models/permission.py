from PyQt6 import QtSql

from common.auth import hash_password
from common.model import SqliteModel
from configs import DATABASE_NAME
from sql_statements.permission import ADD_PERMISSION_SQL, ASSIGN_PERMISSION_SQL, VERIFY_PERMISSION_SQL, \
    PERMISSION_USER_VIEW_SQL, CREATE_PERMISSION_TABLE_SQL, CREATE_PERMISSION_USER_TABLE_SQL


class PermissionModel(SqliteModel):
    def __init__(self, database_name=DATABASE_NAME, table_create_sql=CREATE_PERMISSION_TABLE_SQL,
                 junction_table_sql=CREATE_PERMISSION_USER_TABLE_SQL):
        self._junction_table_sql = junction_table_sql
        super().__init__(database_name, table_create_sql)

    def init_db(self):
        super().init_db()  # Initialize the main table

        # Create the junction table
        junction_query = QtSql.QSqlQuery()
        if not junction_query.exec(self._junction_table_sql):
            raise Exception(f"Failed to create junction table: {junction_query.lastError().text()}")

    def add_permission(self, permission):
        """Add a new permission to the permissions table."""
        query = QtSql.QSqlQuery()
        query.prepare(ADD_PERMISSION_SQL)
        query.addBindValue(permission)
        if not query.exec():
            raise Exception(f"Error adding permission: {query.lastError().text()}")

    def assign_permission_to_user(self, user_id, permission_id):
        """Link a user to a permission in the junction table."""
        query = QtSql.QSqlQuery()
        query.prepare(ASSIGN_PERMISSION_SQL)
        query.addBindValue(user_id)
        query.addBindValue(permission_id)
        if not query.exec():
            raise Exception(f"Error assigning permission: {query.lastError().text()}")

    def verify_permission(self, username, required_permission):
        """Verify if a user has a specific permission."""
        query = QtSql.QSqlQuery()
        query.prepare(VERIFY_PERMISSION_SQL)
        query.addBindValue(username)
        query.addBindValue(required_permission)

        if query.exec() and query.next():
            return True
        return False

    def fetch_user_permissions(self):
        """Fetch all usernames and their permissions."""
        query = QtSql.QSqlQuery(PERMISSION_USER_VIEW_SQL)

        results = []
        while query.next():
            username = query.value(0)  # Username
            permission = query.value(1)  # Permission
            results.append((username, permission))

        return results
