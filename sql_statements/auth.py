CREATE_USER_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_superuser BOOLEAN NOT NULL
    )
'''

# AUTH SQL STATEMENTS
INSERT_USER_SQL = "INSERT OR IGNORE INTO users (username, password, is_superuser) VALUES (?, ?, ?)"

VERIFY_USER_SQL = "SELECT password FROM users WHERE username = ?"

VERIFY_ADMIN_USER_SQL = "SELECT is_superuser FROM users WHERE username = ?"



