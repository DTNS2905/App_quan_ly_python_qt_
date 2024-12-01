import sqlite3
from dataclasses import dataclass

from common.model import NativeSqlite3Model
from configs import DATABASE_NAME
from sql_statements.permission import ADD_PERMISSION_SQL, \
    PERMISSION_USER_VIEW_SQL, CREATE_PERMISSION_TABLE_SQL, CREATE_PERMISSION_USER_TABLE_SQL, \
    GET_PERMISSION_BY_USERNAME_SQL, ASSIGN_PERMISSION_BY_USERNAME_SQL


@dataclass
class PermissionDTO:
    username: str
    permissions: list[str]
    is_admin: bool = False


class PermissionModel(NativeSqlite3Model):
    _junction_table_sql = CREATE_PERMISSION_USER_TABLE_SQL
    _add_permission_sql = ADD_PERMISSION_SQL
    _assign_permission_sql = ASSIGN_PERMISSION_BY_USERNAME_SQL
    _get_permission_by_username = GET_PERMISSION_BY_USERNAME_SQL
    _fetch_user_permission_sql = PERMISSION_USER_VIEW_SQL

    def __init__(self, database_name=DATABASE_NAME, table_create_sql=CREATE_PERMISSION_TABLE_SQL):
        super().__init__(database_name, table_create_sql)
        self.init_junction_table()

    def init_junction_table(self):
        cur = self.connection.cursor()
        try:
            cur.execute(self._junction_table_sql)
            self.connection.commit()
        except sqlite3.Error as error:
            raise Exception(f"Failed to create junction table: {error}")
        finally:
            cur.close()

    def assign_permission_to_user(self, username, permission):
        """Link a user to a permission in the junction table."""
        cur = self.connection.cursor()
        cur.execute(self._assign_permission_sql, (permission, username))
        if cur.rowcount > 0:
            self.connection.commit()
            cur.close()
            print(f"assigning permission '{permission}' to '{username}' successfully")
        else:
            self.connection.rollback()
            cur.close()
            raise Exception(f"Error assigning permission '{permission}' to '{username}' successfully")

    def get_permission_by_username(self, username: str):
        """Verify if a user has a specific permission."""
        cur = self.connection.cursor()
        cur.execute(self._get_permission_by_username, (username,))
        rows = cur.fetchall()
        cur.close()
        return PermissionDTO(username, [r[0] for r in rows], "admin" in username)

    def fetch_user_permissions(self) -> list[PermissionDTO]:
        """Fetch all usernames and their permissions."""
        cur = self.connection.cursor()
        cur.execute(self._fetch_user_permission_sql)
        rows = cur.fetchall()
        data: list[PermissionDTO] = []
        raw_data: dict[str, list[str]] = {}
        for row in rows:
            username = row[0]
            permission = row[1]
            if username not in raw_data.keys():
                raw_data[username] = [permission]
            else:
                raw_data[username].append(permission)
        for username, permissions in raw_data.items():
            data.append(PermissionDTO(username, permissions, "admin" in username))
        cur.close()
        return data

    def add_permission(self, permission):
        """Add a single permission to the database."""
        cur = self.connection.cursor()
        cur.execute(self._add_permission_sql, (permission,))
        if cur.rowcount > 0:
            self.connection.commit()
            cur.close()
            print(f"Add permission '{permission}' successfully")
        else:
            self.connection.rollback()
            cur.close()
            raise Exception(f"Error adding permission '{permission}'")


if __name__ == "__main__":
    model = PermissionModel(database_name=r'D:\freelances\Tuan\app_quan_ly_python_qt\app_quan_ly_pyqt6.db')
    # model.add_permission("test")
    model.assign_permission_to_user("admin", "file:view")
    # print(model.fetch_user_permissions())
    # print(model.get_permission_by_username("admin"))
