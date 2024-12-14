import sqlite3
from datetime import datetime, timedelta

import pytz

from common.model import NativeSqlite3Model
from common.time import convert_utc_time_to_timezone
from configs import DATABASE_NAME
from messages.assignment import CURRENT_ASSIGNMENT, PRE_ASSIGNMENT, POST_ASSIGNMENT
from sql_statements.assignment import ADD_DEADLINE_FOR_ITEM, CREATE_ASSIGNMENT_TABLE


class AssignmentModel(NativeSqlite3Model):
    _add_deadline_for_item = ADD_DEADLINE_FOR_ITEM
    _create_assignment_table = CREATE_ASSIGNMENT_TABLE
    _fetch_assignment_query = """
            SELECT a.assignment_name, a.start_time, a.end_time
            FROM assignments a
            JOIN users u ON u.id = a.assigned_to OR u.id = a.assigned_by
            WHERE u.username = ?
        """

    def __init__(
            self, database_name=DATABASE_NAME, table_create_sql=_create_assignment_table
    ):
        super().__init__(database_name, table_create_sql)

    def add_deadline(self, assignment_name, item_name, assigned_by_name, assigned_to_name, start_time, end_time):
        """
        Adds a deadline to the database after resolving user_id and item_id.

        :param assignment_name: The name of the assignment.
        :param item_name: The name of the item.
        :param assigned_by_name: The name of the assigning user.
        :param assigned_to_name: The name of the assigned user.
        :param start_time: The start time (ISO format).
        :param end_time: The end time (ISO format).
        :raises ValueError: If any of the identifiers are invalid.
        :raises Exception: For database-related issues.
        """
        try:
            # Resolve item_id and user_ids
            item_id = self.get_item_id_by_name(item_name)
            assigned_by = self.get_user_id_by_name(assigned_by_name)
            assigned_to = self.get_user_id_by_name(assigned_to_name)

            # Insert into assignments table
            with self.connection as conn:
                cur = conn.cursor()
                try:
                    cur.execute(self._add_deadline_for_item,
                                (assignment_name, item_id, assigned_by, assigned_to, start_time, end_time))
                finally:
                    cur.close()
        except ValueError as ve:
            raise ValueError(f"Invalid input: {ve}")
        except sqlite3.Error as e:
            raise Exception(f"Database operation failed: {e}")

    def fetch_assignment(self, user_name):
        try:
            with self.connection as conn:
                cur = conn.cursor()
                try:
                    cur.execute(self._fetch_assignment_query, (user_name,))
                    return cur.fetchone()
                finally:
                    cur.close()
        except sqlite3.Error as e:
            raise Exception(f"Database operation failed: {e}")

    def get_user_id_by_name(self, user_name):
        """
        Fetches the user_id for the given user_name.

        :param user_name: The name of the user.
        :return: The user_id if found, otherwise raises an exception.
        """
        query = "SELECT id FROM users WHERE username = ?"
        try:
            with self.connection as conn:
                cur = conn.cursor()
                try:
                    cur.execute(query, (user_name,))
                    result = cur.fetchone()
                    if result:
                        return result[0]
                    else:
                        raise ValueError(f"No user found with name '{user_name}'.")
                finally:
                    cur.close()
        except sqlite3.Error as e:
            raise Exception(f"Database operation failed: {e}")

    def get_item_id_by_name(self, item_name):
        """
        Fetches the item_id for the given item_name.

        :param item_name: The name of the item.
        :return: The item_id if found, otherwise raises an exception.
        """
        query = "SELECT id FROM items WHERE original_name = ?"
        try:
            with self.connection as conn:
                cur = conn.cursor()
                try:
                    cur.execute(query, (item_name,))
                    result = cur.fetchone()
                    if result:
                        return result[0]
                    else:
                        raise ValueError(f"No item found with name '{item_name}'.")
                finally:
                    cur.close()
        except sqlite3.Error as e:
            raise Exception(f"Database operation failed: {e}")

