CREATE_ASSIGNMENT_TABLE = '''
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assignment_name TEXT NOT NULL,
    item_id INTEGER NOT NULL,
    assigned_by INTEGER NOT NULL,
    assigned_to INTEGER NOT NULL,
    start_time TEXT NOT NULL CHECK (start_time LIKE '____-__-__ __:__:__'),
    end_time TEXT NOT NULL CHECK (end_time LIKE '____-__-__ __:__:__' AND end_time > start_time),
    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE CASCADE
);

'''

ADD_DEADLINE_FOR_ITEM = '''
INSERT INTO assignments (assignment_name,item_id, assigned_by, assigned_to, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?)
 '''

GET_TIME_STATUS_BASED_ON_USERNAME_AND_ASSIGNMENT_ID = """
        SELECT a.begin_time, a.end_time
        FROM assignments AS a
        JOIN users AS u
        ON a.assigned_by = u.user_id OR a.assigned_to = u.user_id
        WHERE a.assignment_id = ? AND u.user_name = ?
"""

GET_TIME_STATUS_BASED_ON_ITEM_ID_AND_USERNAME = """
        SELECT a.begin_time, a.end_time
        FROM assignments AS a
        JOIN users AS u
        ON a.assigned_by = u.user_id OR a.assigned_to = u.user_id
        WHERE a.assignment_id = ? AND u.user_name = ?
"""


