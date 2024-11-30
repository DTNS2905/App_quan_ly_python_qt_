CREATE_PERMISSION_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        permission TEXT UNIQUE NOT NULL
    )
'''

CREATE_PERMISSION_USER_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS user_permissions (
        user_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, permission_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE
    )
'''

ADD_PERMISSION_SQL = "INSERT OR IGNORE INTO permissions (permission) VALUES (?)"

ASSIGN_PERMISSION_SQL = "INSERT OR IGNORE INTO user_permissions (user_id, permission_id) VALUES (?, ?)"

VERIFY_PERMISSION_SQL = '''
    SELECT p.permission
    FROM users u
    INNER JOIN user_permissions up ON u.id = up.user_id
    INNER JOIN permissions p ON up.permission_id = p.id
    WHERE u.username = ? AND p.permission = ?
'''

REMOVE_PERMISSION_FROM_USER_SQL = '''
    DELETE FROM user_permissions
    WHERE user_id = (SELECT id FROM users WHERE username = ?)
    AND permission_id = (SELECT id FROM permissions WHERE permission = ?)
'''
UPDATE_PERMISSION_SQL = '''
    INSERT OR IGNORE INTO user_permissions (user_id, permission_id)
        VALUES (
            (SELECT id FROM users WHERE username = ?),
            (SELECT id FROM permissions WHERE permission = ?)
        )
'''

PERMISSION_USER_VIEW_SQL = '''
    CREATE VIEW IF NOT EXISTS user_permissions_view AS
    SELECT 
        u.username,
        p.permission
    FROM 
        user_permissions up
    JOIN users u ON up.user_id = u.id
    JOIN permissions p ON up.permission_id = p.id;
'''

