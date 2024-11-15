from PyQt5 import QtSql
import bcrypt


class AuthModel:
    def __init__(self):
        self.db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("my_database.db")
        if not self.db.open():
            raise Exception(f"Database error: {self.db.lastError().text()}")

        self.init_db()

    def init_db(self):
        query = QtSql.QSqlQuery()
        query.exec_('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')

    def add_user(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query = QtSql.QSqlQuery()
        query.prepare("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)")
        query.addBindValue(username)
        query.addBindValue(hashed_password)
        if not query.exec_():
            print(f"Error adding user: {query.lastError().text()}")

    def verify_user(self, username):
        query = QtSql.QSqlQuery()
        query.prepare("SELECT password FROM users WHERE username = ?")
        query.addBindValue(username)
        if query.exec_() and query.next():
            return query.value(0)
        return None

    def close_connection(self):
        self.db.close()
        QtSql.QSqlDatabase.removeDatabase("QSQLITE")
