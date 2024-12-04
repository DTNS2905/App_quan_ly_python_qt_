import sqlite3
from dataclasses import dataclass

from common.model import NativeSqlite3Model
from configs import DATABASE_NAME
from sql_statements.log import CREATE_TABLE_SQL


@dataclass
class LogDto:
    id: int
    user_id: int
    message: str
    created_at: str
    updated_at: str


class LogModel(NativeSqlite3Model):
    _fetch_sql = """
        SELECT id, user_id, message, created_at, updated_at FROM logs
    """

    def __init__(self, database_name=DATABASE_NAME, table_create_sql=CREATE_TABLE_SQL):
        super().__init__(database_name, table_create_sql)

    def fetch_log(self):
        cur = self.connection.cursor()
        cur.execute(self._fetch_sql)
        data = cur.fetchone()
        return LogDto(*data)

    @staticmethod
    def write_log(username, message):
        connection = sqlite3.connect(DATABASE_NAME)
        cur = connection.cursor()
        try:
            cur.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_id = cur.fetchone()[0]
            cur.execute("insert into logs (user_id, message) values (?, ?)",
                        (user_id, message))
            if cur.rowcount > 0:
                connection.commit()
                print(f"Log for user '{username}' successfully")
            else:
                connection.rollback()
                print(f"Error: Log for user '{username}' failed")
        except Exception as e:
            print(f"Error: Log for user '{username}' failed: {str(e)}")
        finally:
            cur.close()
            connection.close()


    def search_log(self, message_pattern):
        cur = self.connection.cursor()
        cur.execute("SELECT id, user_id, message, created_at, updated_at FROM logs WHERE message LIKE %?%",
                    (message_pattern,))
        return [LogDto(*item) for item in cur.fetchall()]

    def get_log_for_user(self, username):
        cur = self.connection.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cur.fetchone()[0]
        cur.execute("SELECT id, user_id, message, created_at, updated_at FROM logs WHERE user_id = ?",
                    (user_id,))
        return [LogDto(*item) for item in cur.fetchall()]
