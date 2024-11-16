CREATE_USER_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
'''

INSERT_USER_SQL = "INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)"

VERIFY_USER_SQL = "SELECT password FROM users WHERE username = ?"

