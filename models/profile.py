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
            print(f"Create profile for user '{username}' successfully")
            return cur.lastrowid
        else:
            self.connection.rollback()
            cur.close()
            raise Exception(f"Error: create profile for user '{username}' failed")

    def update(self, username, attribute, value):
        if attribute not in ["user_id", "fullname", "position", "phone_number"]:
            raise Exception(f"Error: update profile for user '{username}' failed")

        cur = self.connection.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cur.fetchone()[0]
        cur.execute(f"update profiles set {attribute}=? where user_id=?",
                    (value, user_id))
        if cur.rowcount > 0:
            self.connection.commit()
            cur.close()
            print(f"Update profile for user '{username}' successfully")
            return cur.lastrowid
        else:
            self.connection.rollback()
            cur.close()
            raise Exception(f"Error: update profile for user '{username}' failed")


if __name__ == "__main__":
    model = ProfileModel(database_name=r'D:\freelances\Tuan\app_quan_ly_python_qt\app_quan_ly_pyqt6.db')
    print(model.get_profile_by_username("admin"))
