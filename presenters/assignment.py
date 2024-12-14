import datetime
import logging

from common.presenter import Presenter
from messages.assignment import PRE_ASSIGNMENT, CURRENT_ASSIGNMENT, POST_ASSIGNMENT
from models.assignment import AssignmentModel


class AssignmentPresenter(Presenter):
    def __init__(self, view):
        super().__init__(view, AssignmentModel())

    def set_deadline(self, assignment_name, item_name, assigned_by_name, assigned_to_name, begin_time, end_time, timezone="Asia/Bangkok"):
        # Retrieve the file name from the QStandardItemModel

        # Validate input
        begin_time_dt, end_time_dt = self._validate_deadline_input(begin_time, end_time)

        # Convert times to timezone
        begin_time_iso, end_time_iso = self._convert_times_to_timezone(begin_time_dt, end_time_dt, timezone)

        # Call model to save the data
        self.model.add_deadline(assignment_name, item_name, assigned_by_name, assigned_to_name, begin_time_iso, end_time_iso)

    def get_time_status(self, assignment_id, user_name):
        # Fetch assignment data
        result = self.model.fetch_assignment(assignment_id, user_name)
        if not result:
            logging.error(f"No assignment found with ID {assignment_id} for user {user_name}.")
            self.view.display_error(f"Lỗi không thể lấy được thời gian cho tài liệu và tệp")
            raise ValueError(f"No assignment found with ID {assignment_id} for user {user_name}.")

        assignment_name, start_time, end_time = result

        # Compute status and time left
        now = datetime.now()
        start_time_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_time_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        status, time_left = self._determine_assignment_status(now, start_time_dt, end_time_dt)

        # Return raw data for presenter
        return {
            "assignment_name": assignment_name,
            "start_time": start_time,
            "end_time": end_time,
            "status": status,
            "time_left": time_left,
        }

    def _validate_deadline_input(self, begin_time, end_time):
        try:
            begin_time_dt = datetime.strptime(begin_time, "%H:%M %d/%m/%Y")
            end_time_dt = datetime.strptime(end_time, "%H:%M %d/%m/%Y")
            if begin_time_dt >= end_time_dt:
                raise ValueError("begin_time must be before end_time.")
            return begin_time_dt, end_time_dt
        except ValueError:
            raise ValueError("Deadline must be in 'h:m d/m/y' format, e.g., '12:30 01/01/2024'.")

    def _determine_assignment_status(self, now, start_time_dt, end_time_dt):
        if now < start_time_dt:
            return PRE_ASSIGNMENT, end_time_dt - now
        elif start_time_dt <= now <= end_time_dt:
            return CURRENT_ASSIGNMENT, end_time_dt - now
        else:
            return POST_ASSIGNMENT, datetime.timedelta(0)
