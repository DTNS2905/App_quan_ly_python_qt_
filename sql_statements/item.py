CREATE_ITEM_TABLE_SQL = '''
   CREATE TABLE IF NOT EXISTS items
    (
        id            integer not null
            constraint item_pk
                primary key autoincrement,
        code          TEXT    not null
            constraint item_pk2
                unique,
        type          TEXT    not null,
        original_name TEXT    not null,
        created_at    TIMESTAMP default current_timestamp,
        updated_at    TIMESTAMP default current_timestamp,
        parent_id     integer DEFAULT 0
            constraint item_item_id_fk
                references items,
        user_id       integer not null
            constraint item_users_id_fk
                references users
    );
'''

INIT_DATA = """
insert or ignore into items (id, code, type, original_name, parent_id, user_id)
    values (0, 'root', 'folder', 'root', -1, 1);
"""

CREATE_PERMISSION_USER_ITEM_TABLE_SQL = '''
    CREATE TABLE IF NOT EXISTS user_item_permissions (
        user_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        permission_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, item_id, permission_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE,
        FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE
    )
'''

FETCH_NAME_FILE_OR_FOLDER_ON_TEXTCHANGED = '''
    SELECT items.original_name
        FROM items
        JOIN user_item_permissions uip ON items.id = uip.item_id
        JOIN permissions p ON uip.permission_id = p.id
        JOIN users u ON u.id = uip.user_id
        WHERE items.original_name LIKE ?
          AND u.username = ?
          AND p.permission = ?
'''




