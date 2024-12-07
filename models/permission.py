import sqlite3
from dataclasses import dataclass

from common.model import NativeSqlite3Model
from configs import DATABASE_NAME
from sql_statements.permission import ADD_PERMISSION_SQL, \
    PERMISSION_USER_VIEW_SQL, CREATE_PERMISSION_TABLE_SQL, CREATE_PERMISSION_USER_TABLE_SQL, \
    GET_PERMISSION_BY_USERNAME_SQL, ASSIGN_PERMISSION_BY_USERNAME_SQL, REMOVE_PERMISSION_FROM_USER_SQL, \
    ASSIGN_PERMISSION_AND_USER_FOR_ITEM_SQL, GET_USER_ID_SQL, GET_PERMISSION_ID_SQL, GET_ITEM_PERMISSION_BY_USERNAME_SQL


@dataclass
class PermissionDTO:
    username: str
    permissions: list[str]
    is_admin: bool = False


@dataclass
class PermissionItemDTO:
    username: str
    permissions: dict[str, list[str]]


@dataclass
class PermissionTableDTO:
    username: str
    fullname: str
    position: str
    phone_number: str
    permissions: list[str]
    is_admin: bool = False


class PermissionModel(NativeSqlite3Model):
    _junction_table_sql = CREATE_PERMISSION_USER_TABLE_SQL
    _add_permission_sql = ADD_PERMISSION_SQL
    _assign_permission_sql = ASSIGN_PERMISSION_BY_USERNAME_SQL
    _get_permission_by_username = GET_PERMISSION_BY_USERNAME_SQL
    _get_item_permission_by_username = GET_ITEM_PERMISSION_BY_USERNAME_SQL
    _fetch_user_permission_sql = PERMISSION_USER_VIEW_SQL
    _remove_permission_from_user_sql = REMOVE_PERMISSION_FROM_USER_SQL
    _get_user_id_sql = GET_USER_ID_SQL
    _get_permission_id_sql = GET_PERMISSION_ID_SQL

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

    def get_item_permission_by_username(self, username: str):
        cur = self.connection.cursor()
        cur.execute(self._get_item_permission_by_username, (username,))
        rows = cur.fetchall()
        permissions: dict[str, list[str]] = {}
        for item, permission in rows:
            if item not in permissions.keys():
                permissions[item] = [permission]
            else:
                permissions[item].append(permission)
        cur.close()
        return PermissionItemDTO(username, permissions)

    def fetch_user_permissions(self) -> list[PermissionTableDTO]:
        """Fetch all usernames and their permissions."""
        cur = self.connection.cursor()
        cur.execute(self._fetch_user_permission_sql)
        rows = cur.fetchall()
        data: list[PermissionTableDTO] = []
        raw_data: dict[str, dict[str, list[str]]] = {}
        for row in rows:
            username, fullname, phone_number, position, permission = row
            if username not in raw_data.keys():
                raw_data[username] = {
                    "infos": [fullname, phone_number, position],
                    "permissions": [permission] if permission is not None else [""]
                }
            else:
                raw_data[username]["permissions"].append(permission if permission is not None else "")
        for username, value in raw_data.items():
            infos = value["infos"]
            permissions = value["permissions"]
            data.append(PermissionTableDTO(username, *infos, permissions=permissions, is_admin="admin" in username))
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

    def unassign_permission_from_user(self, username, permission):
        """Unassign a permission from a user using their IDs."""
        cur = self.connection.cursor()
        try:
            cur.execute(self._remove_permission_from_user_sql, (username, permission))
            print(cur.rowcount)
            if cur.rowcount > 0:
                self.connection.commit()
                print(f"Unassigned permission '{permission}' from '{username}' successfully")
            else:
                self.connection.rollback()
                raise Exception(f"Error unassigning permission '{permission}' from '{username}'")
        finally:
            cur.close()

    def get_user_id_by_username(self, username):
        """Get user_id from username."""
        cur = self.connection.cursor()
        cur.execute(self._get_user_id_sql, (username,))
        result = cur.fetchone()
        cur.close()
        if result:
            return result[0]
        else:
            raise Exception(f"User '{username}' not found.")

    def delete_user_by_username(self, username):
        cur = self.connection.cursor()
        try:
            cur.execute("DELETE FROM users WHERE username=?", (username,))
            if cur.rowcount > 0:
                self.connection.commit()
                print(f"Delete '{username}' successfully")
            else:
                self.connection.rollback()
                raise Exception(print(f"Delete '{username}' failed"))
        finally:
            cur.close()

    def get_permission_id_by_name(self, permission):
        """Get permission_id from permission name."""
        cur = self.connection.cursor()
        cur.execute(self._get_permission_id_sql, (permission,))
        result = cur.fetchone()
        cur.close()
        if result:
            return result[0]
        else:
            raise Exception(f"Permission '{permission}' not found.")

    def get_permission_by_username(self, username: str):
        """Verify if a user has specific permissions."""
        cur = self.connection.cursor()
        cur.execute(self._get_permission_by_username, (username,))
        rows = cur.fetchall()
        cur.close()
        return PermissionDTO(username, [r[0] for r in rows], "admin" in username)

    def assign_permissions_to_users_for_file(self, item_name, users, permissions):
        """
        Assign multiple users and permissions to a single file.

        :param db_path: Path to the SQLite database.
        :param item_name: The name of the file (original_name in the items table).
        :param users: List of usernames to assign permissions to.
        :param permissions: List of permission names to assign.
        """

        cur = self.connection.cursor()

        try:
            # Fetch item_id using the item's original name
            cur.execute("SELECT id FROM items WHERE original_name = ?", (item_name,))
            item = cur.fetchone()
            if not item:
                print(f"Item '{item_name}' not found.")
                return
            item_id = item[0]

            # Iterate over users and permissions
            for username in users:
                # Fetch user_id using the username
                cur.execute("SELECT id FROM users WHERE username = ?", (username,))
                user = cur.fetchone()
                if not user:
                    print(f"User '{username}' not found. Skipping...")
                    continue
                user_id = user[0]

                for permission_name in permissions:
                    # Fetch permission_id using the permission name
                    cur.execute("SELECT id FROM permissions WHERE permission = ?", (permission_name,))
                    permission = cur.fetchone()
                    if not permission:
                        print(f"Permission '{permission_name}' not found. Skipping...")
                        continue
                    permission_id = permission[0]

                    # Insert into user_item_permissions
                    try:
                        cur.execute(ASSIGN_PERMISSION_AND_USER_FOR_ITEM_SQL, (item_id, user_id, permission_id))
                    except sqlite3.IntegrityError as e:
                        print(f"Skipping duplicate assignment: {e}")

            # Commit the transaction
            cur.commit()
            print(f"Permissions successfully assigned to users for item '{item_name}'.")

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            # Close the connection
            cur.close()

    def fetch_usernames_based_on_suggestions(self, text):
        """Fetch usernames from the database that match the input."""
        cur = self.connection.cursor()

        try:
            # Use SQL LIKE to match usernames containing the input text
            cur.execute("SELECT username FROM users WHERE username LIKE ?", (f"%{text}%",))
            rows = cur.fetchall()

            # Extract usernames from the result
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            cur.close()


if __name__ == "__main__":
    model = PermissionModel(database_name=r'D:\freelances\Tuan\app_quan_ly_python_qt\app_quan_ly_pyqt6.db')
    # model.add_permission("test")
    # model.assign_permission_to_user("admin", "file:view")
    # print(model.fetch_user_permissions())
    # print(model.get_permission_by_username("admin"))
    print(model.get_item_permission_by_username("admin"))
