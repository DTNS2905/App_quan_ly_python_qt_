CREATE_TABLE_SQL = '''
   CREATE TABLE IF NOT EXISTS logs
    (
        id            integer not null
            constraint log_pk
                primary key autoincrement,
        user_id       integer not null,
        message       TEXT    not null,
        created_at    TIMESTAMP default current_timestamp,
        updated_at    TIMESTAMP default current_timestamp
    );
'''