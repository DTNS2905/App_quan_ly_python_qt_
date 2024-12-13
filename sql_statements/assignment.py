CREATE_ASSIGNMENT_TABLE = '''
CREATE TABLE assignments (
      assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    assigned_by INTEGER NOT NULL,
    assigned_to INTEGER NOT NULL,
    begin_time TEXT NOT NULL CHECK (begin_time LIKE '____-__-__ __:__:__'),
    end_time TEXT NOT NULL CHECK (end_time LIKE '____-__-__ __:__:__'),
    FOREIGN KEY (item_id) REFERENCES items(item_id),
    FOREIGN KEY (assigned_by) REFERENCES users(user_id),
    FOREIGN KEY (assigned_to) REFERENCES users(user_id)
);
'''

ADD_DEADLINE_FOR_ITEM = '''
INSERT INTO assignments (item_id, assigned_by, assigned_to, begin_time, end_time) VALUES (?, ?, ?, ?, ?)
 '''

GET_TIME_STATUS_BASED_ON_USERNAME = """
        SELECT a.begin_time, a.end_time
        FROM assignments AS a
        JOIN users AS u
        ON a.assigned_by = u.user_id OR a.assigned_to = u.user_id
        WHERE a.assignment_id = ? AND u.user_name = ?
"""


