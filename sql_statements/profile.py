CREATE_TABLE_SQL = '''
   CREATE TABLE IF NOT EXISTS profiles
    (
        id            integer not null
            constraint profile_pk
                primary key autoincrement,
        user_id       integer not null
            constraint profile_users_id_fk
                references users,
        fullname          TEXT    not null,
        position TEXT    not null,
        phone_number  TEXT    not null,
        created_at    TIMESTAMP default current_timestamp,
        updated_at    TIMESTAMP default current_timestamp
    );
'''

INIT_DATA = """
insert or ignore into profiles (id, user_id, fullname, position, phone_number)
    values (0, 0, 'Admin', 'admin', '0987654321');
"""