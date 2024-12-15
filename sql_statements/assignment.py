CREATE_ASSIGNMENT_TABLE = '''
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_name TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    assigned_by INTEGER NOT NULL,
    assigned_to INTEGER NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL CHECK (end_time > start_time),
    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE CASCADE
);

'''

ADD_DEADLINE_FOR_ITEM = '''
INSERT INTO assignments (assignment_name,item_id, assigned_by, assigned_to, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?)
 '''


