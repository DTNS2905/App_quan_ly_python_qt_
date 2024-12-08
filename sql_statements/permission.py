CREATE_PERMISSION_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS permissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        permission TEXT UNIQUE NOT NULL
    )
"""

CREATE_PERMISSION_USER_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS user_permissions (
        user_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, permission_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE
    )
"""

ADD_PERMISSION_SQL = "INSERT OR IGNORE INTO permissions (permission) VALUES (?)"

ASSIGN_PERMISSION_SQL = (
    "INSERT OR IGNORE INTO user_permissions (user_id, permission_id) VALUES (?, ?)"
)

ASSIGN_PERMISSION_BY_USERNAME_SQL = """
    INSERT OR IGNORE INTO user_permissions (user_id, permission_id)
    SELECT u.id, p.id
    FROM users u
    JOIN permissions p ON p.permission = ?
    WHERE u.username = ?;
"""

GET_PERMISSION_BY_USERNAME_SQL = """
    SELECT DISTINCT p.permission
    FROM users u
    INNER JOIN user_permissions up ON u.id = up.user_id
    INNER JOIN permissions p ON up.permission_id = p.id
    WHERE u.username = ?
"""

GET_ITEM_PERMISSION_BY_USERNAME_SQL = """
    SELECT DISTINCT i.original_name, p.permission
    FROM users u
    INNER JOIN user_item_permissions uip ON u.id = uip.user_id
    INNER JOIN items i ON i.id = uip.item_id = i.id
    INNER JOIN permissions p ON uip.permission_id = p.id
    WHERE u.username = ?
"""

REMOVE_PERMISSION_FROM_USER_SQL = """
    DELETE FROM user_permissions
    WHERE user_id = (SELECT id FROM users WHERE username = ?)
    AND permission_id = (SELECT id FROM permissions WHERE permission = ?);
"""

UPDATE_PERMISSION_SQL = """
    INSERT OR IGNORE INTO user_permissions (user_id, permission_id)
        VALUES (
            (SELECT id FROM users WHERE username = ?),
            (SELECT id FROM permissions WHERE permission = ?)
        )
"""

PERMISSION_USER_VIEW_SQL = """
    SELECT
        u.username,
        pr.fullname,
        pr.phone_number,
        pr.position,
        p.permission
    FROM
        users u
    LEFT JOIN user_permissions up ON up.user_id = u.id
    LEFT JOIN profiles pr ON pr.user_id = u.id
    LEFT JOIN permissions p ON up.permission_id = p.id
"""

GET_USER_ID_SQL = "SELECT id FROM users WHERE username = ?;"

GET_PERMISSION_ID_SQL = "SELECT id FROM permissions WHERE permission = ?;"

ASSIGN_PERMISSION_AND_USER_FOR_ITEM_SQL = """
INSERT OR IGNORE INTO user_item_permissions (item_id, user_id, permission_id) VALUES (?, ?, ?);
"""

UNASSIGN_PERMISSION_AND_USER_FOR_ITEM_SQL = """
DELETE FROM user_item_permissions
WHERE item_id = ?
AND user_id = ?
AND permission_id = ?;
"""
