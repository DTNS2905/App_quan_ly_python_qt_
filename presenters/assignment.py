from datetime import datetime, timedelta
import logging

import pytz

import common.time
from common import session
from common.presenter import Presenter
from messages.assignment import PRE_ASSIGNMENT, CURRENT_ASSIGNMENT, POST_ASSIGNMENT
from models.assignment import AssignmentModel
from models.log import LogModel


class AssignmentPresenter(Presenter):
    def __init__(self, view):
        super().__init__(view, AssignmentModel())


    def set_deadline(self, assignment_name, item_name, assigned_by_name, assigned_to_name, start_time, end_time, timezone="Asia/Bangkok"):
        # Retrieve the file name from the QStandardItemModel

        # Validate input
        begin_time_dt, end_time_dt = self._validate_deadline_input(start_time, end_time)

        # Call model to save the data
        self.model.add_deadline(assignment_name, item_name, assigned_by_name, assigned_to_name, begin_time_dt, end_time_dt)

    def get_time_status(self, user_name):
        # Fetch assignment data
        result = self.model.fetch_assignment(user_name)
        if not result:
            logging.error(f"No assignment found for user {user_name}.")
            LogModel.write_log(
                user_name,
                f"Cảnh báo: Không tìm thấy công việc được giao cho người dùng: {user_name}."
            )
            raise ValueError(f"No assignment found for user {user_name}.")

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
            # begin_time_dt = datetime.strptime(begin_time, "%d/%m/%Y %H:%M ")
            # end_time_dt = datetime.strptime(end_time, "%d/%m/%Y %H:%M ")

            begin_time_dt = begin_time
            end_time_dt = end_time

            if begin_time_dt >= end_time_dt:
                raise ValueError("begin_time must be before end_time.")
            return begin_time_dt, end_time_dt
        except ValueError:
            raise ValueError("Deadline must be in 'd/m/y h:m ' format, e.g., ' 01/01/2024 12:30'.")

    def _determine_assignment_status(self, now, start_time_dt, end_time_dt):
        if now < start_time_dt:
            return PRE_ASSIGNMENT, end_time_dt - now
        elif start_time_dt <= now <= end_time_dt:
            return CURRENT_ASSIGNMENT, end_time_dt - now
        else:
            return POST_ASSIGNMENT, timedelta(0)

    def _convert_times_to_timezone(self, begin_time_dt, end_time_dt, timezone):
        begin_time_utc = begin_time_dt.replace(tzinfo=pytz.utc)
        end_time_utc = end_time_dt.replace(tzinfo=pytz.utc)

        begin_time_converted = common.time.convert_utc_time_to_timezone(begin_time_utc.isoformat(), zone=timezone)
        end_time_converted = common.time.convert_utc_time_to_timezone(end_time_utc.isoformat(), zone=timezone)

        return begin_time_converted.strftime("%Y-%m-%d %H:%M"), end_time_converted.strftime("%Y-%m-%d %H:%M")

    def remind_if_no_time_left(self, user_name):
        """
        Checks the assignment's time status and reminds the user via a message box if no time is left.
        """
        try:
            # Fetch the time status for the assignment
            status_data = self.get_time_status(user_name)

            # Check if there is no time left
            time_left = status_data["time_left"]
            if isinstance(time_left, timedelta) and time_left <= timedelta(0):
                # Show reminder message box
                self.view.display_success(
                    f"Không còn thời gian cho công việc: '{status_data['assignment_name']}'!",
                )

        except ValueError as e:
            logging.error(f"Failed to check time status: {e}")
            LogModel.write_log(
                session.SESSION.get_username(),
                "Cảnh báo: Không thể kiểm tra thời gian còn lại cho tài liệu."
            )
