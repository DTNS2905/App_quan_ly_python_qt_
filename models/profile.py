import logging
import sqlite3
from dataclasses import dataclass

from common.model import NativeSqlite3Model
from configs import DATABASE_NAME
from sql_statements.profile import CREATE_TABLE_SQL, INIT_DATA


@dataclass
class ProfileDto:
    id: int
    user_id: int
    fullname: str
    position: int
    phone_number: str
    created_at: str
    updated_at: str


class ProfileModel(NativeSqlite3Model):
    _create_table_sql = CREATE_TABLE_SQL
    _fetch_sql = """
        SELECT p.id, p.user_id, p.fullname, p.position, p.phone_number, p.created_at, p.updated_at FROM profiles AS p
        WHERE user_id = ?
    """
    _init_data_sql = INIT_DATA

    def __init__(self, database_name=DATABASE_NAME, table_create_sql=CREATE_TABLE_SQL):
        super().__init__(database_name, table_create_sql)
        self._init_data()

    def _init_data(self):
        cur = self.connection.cursor()
        try:
            cur.execute(self._init_data_sql)
            self.connection.commit()
        except sqlite3.Error as error:
            raise Exception(f"Failed to init data: {error}")
        finally:
            cur.close()

    def get_profile_by_username(self, username):
        cur = self.connection.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cur.fetchone()[0]
        stm = f"SELECT id, user_id, fullname, position, phone_number, created_at, updated_at FROM profiles WHERE user_id={user_id}"
        cur.execute(stm)
        data = cur.fetchone()
        if data is None:
            return None  # Return None if no profile data is found

        return ProfileDto(*data)

    def create(self, username, fullname, position, phone_number):
        cur = self.connection.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cur.fetchone()[0]
        cur.execute("insert into profiles (user_id, fullname, position, phone_number) values (?, ?, ?, ?)",
                    (user_id, fullname, position, phone_number))
        if cur.rowcount > 0:
            self.connection.commit()
            cur.close()
            logging.info(f"Create profile for user '{username}' successfully")
            return cur.lastrowid
        else:
            self.connection.rollback()
            cur.close()
            raise Exception(f"Error: create profile for user '{username}' failed")

    def update(self, username, attribute, value):
        # Validate attribute
        if attribute not in ["user_id", "fullname", "position", "phone_number"]:
            raise ValueError(f"Error: update profile for user '{username}' failed. Invalid attribute '{attribute}'.")

        cur = self.connection.cursor()

        try:
            # Fetch user_id for the given username
            cur.execute("SELECT id FROM users WHERE username = ?", (username,))
            user = cur.fetchone()
            if user is None:
                raise ValueError(f"Error: User '{username}' not found.")
            user_id = user[0]

            # Perform the update
            cur.execute(f"UPDATE profiles SET {attribute} = ? WHERE user_id = ?", (value, user_id))

            # Commit or rollback based on the operation
            if cur.rowcount == 0:
                # Either no matching user_id, or no change in the value
                self.connection.rollback()
                raise ValueError(f"Error: Update failed for user '{username}'. No changes made.")

            self.connection.commit()
            logging.info(f"Update profile for user '{username}' successfully.")
            return True  # Return True to indicate success

        except Exception as e:
            # Handle exceptions and rollback
            self.connection.rollback()
            raise e

        finally:
            # Ensure the cursor is always closed
            cur.close()


if __name__ == "__main__":
    model = ProfileModel(database_name=r'D:\freelances\Tuan\app_quan_ly_python_qt\app_quan_ly_pyqt6.db')
