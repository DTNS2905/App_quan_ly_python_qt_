import sqlite3
from datetime import datetime, timedelta

from common.model import NativeSqlite3Model
from configs import DATABASE_NAME
from messages.assignment import CURRENT_ASSIGNMENT, PRE_ASSIGNMENT, POST_ASSIGNMENT
from sql_statements.assignment import ADD_DEADLINE_FOR_ITEM, CREATE_ASSIGNMENT_TABLE, GET_TIME_STATUS_BASED_ON_USERNAME


class AssignmentModel(NativeSqlite3Model):
    _add_deadline_for_item = ADD_DEADLINE_FOR_ITEM
    _create_assignment_table = CREATE_ASSIGNMENT_TABLE
    _get_time_status_based_on_username = GET_TIME_STATUS_BASED_ON_USERNAME

    def __init__(
            self, database_name=DATABASE_NAME, table_create_sql=_create_assignment_table
    ):
        super().__init__(database_name, table_create_sql)

    def set_deadline(self, item_id, assigned_by, assigned_to, begin_time, end_time):
        """
        Sets a deadline for an item by adding an entry to the database.

        :param item_id: The ID of the item (integer).
        :param assigned_by: The user assigning the item (integer).
        :param assigned_to: The user to whom the item is assigned (integer).
        :param begin_time: The deadline for the assignment in dd/mm/yyyy hh:mm format (string).
        :param end_time: The deadline for the assignment in dd/mm/yyyy hh:mm format (string).
        :raises ValueError: If any input is invalid or deadline format is incorrect.
        :raises Exception: For database-related issues.
        """
        # Validate input types
        if not all(isinstance(arg, int) for arg in [item_id, assigned_by, assigned_to]):
            raise ValueError("item_id, assigned_by, and assigned_to must be integers.")

        # Parse and validate deadline format
        try:
            begin_time_iso = datetime.strptime(begin_time, "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")
            end_time_iso = datetime.strptime(end_time, "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("Deadline must be in dd/mm/yyyy hh:mm format.")

        query = self._add_deadline_for_item

        # Perform the database operation
        try:
            with self.connection as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (item_id, assigned_by, assigned_to, begin_time_iso,end_time_iso))
        except sqlite3.Error as e:
            raise Exception(f"Database operation failed: {e}")

    def get_time_status(self, assignment_id, user_name):
        """
        Fetches the timing information for the given assignment ID and user name, checks status, and calculates time left.

        :param assignment_id: The ID of the assignment (integer).
        :param user_name: The name of the user assigning or being assigned (string).
        :return: A dictionary with begin_time, end_time, status, and time_left.
        :raises ValueError: If the assignment_id or user_name is not valid, or the assignment doesn't exist.
        :raises Exception: For database-related issues.
        """
        if not isinstance(assignment_id, int):
            raise ValueError("assignment_id must be an integer.")
        if not isinstance(user_name, str):
            raise ValueError("user_name must be a string.")

        # Query to fetch the timing information and verify user involvement
        query = GET_TIME_STATUS_BASED_ON_USERNAME

        try:
            with self.connection as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (assignment_id, user_name))
                    result = cur.fetchone()

            if not result:
                raise ValueError(f"No assignment found with ID {assignment_id} for user {user_name}.")

            begin_time, end_time = result
            now = datetime.now()

            # Parse the datetime fields
            begin_time_dt = datetime.strptime(begin_time, "%Y-%m-%d %H:%M:%S")
            end_time_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

            # Calculate time left until the end_time
            time_left = end_time_dt - now

            # Determine status
            if now < begin_time_dt:
                status = PRE_ASSIGNMENT
            elif begin_time_dt <= now <= end_time_dt:
                status = CURRENT_ASSIGNMENT
            else:
                status = POST_ASSIGNMENT

            # Prepare response
            response = {
                "user_name": user_name,
                "begin_time": begin_time,
                "end_time": end_time,
                "status": status,
                "time_left": str(time_left) if time_left > timedelta(0) else "No Time Left",
            }

            return response

        except sqlite3.Error as e:
            raise Exception(f"Database operation failed: {e}")

