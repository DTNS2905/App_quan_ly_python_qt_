import logging
from datetime import datetime

from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMessageBox

from common import session
from common.session import UserSession
from configs import ADD_DEADLINE_PATH
from models.log import LogModel
from presenters.assignment import AssignmentPresenter
from presenters.profile import ProfilePresenter
from ui_components.custom_messgae_box import CustomMessageBox


class AssignmentDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(ADD_DEADLINE_PATH, self)

        self.selected_item = None  # Store the selected item name
        self.assignment_presenter = AssignmentPresenter(self)
        self.profile_presenter = ProfilePresenter(self)

        self.perform_button.clicked.connect(self.handle_submit)

    def handle_submit(self):
        # Collect inputs
        assignment_name = self.assignment_input.text()
        assigned_by_name = session.SESSION.get_username()
        assigned_to_name = self.username_input.text()
        item_name = self.selected_item
        start_time = self.start_time_input.dateTime().toString("HH:mm dd/MM/yyyy")
        end_time = self.end_time_input.dateTime().toString("HH:mm dd/MM/yyyy")

        # Validation
        try:
            # Parse start_time and end_time to datetime objects
            start_time_dt = datetime.strptime(start_time, "%H:%M %d/%m/%Y")
            end_time_dt = datetime.strptime(end_time, "%H:%M %d/%m/%Y")

            # Ensure start_time is earlier than end_time
            if start_time_dt >= end_time_dt:
                raise ValueError("Thời gian bắt đầu phải sớm hơn thời gian kết thúc")

            # Optionally ensure both times are in the future
            now = datetime.now()
            if start_time_dt <= now:
                raise ValueError("Thời gian bắt đâu phải tính từ hiện tại")
            if end_time_dt <= now:
                raise ValueError("Thời gian kết thúc phải tính từ hiện tại")

            # Proceed to set the deadline
            self.assignment_presenter.set_deadline(
                assignment_name, item_name, assigned_by_name, assigned_to_name, start_time, end_time
            )
            self.display_success(f"Hạn chót được thêm thành công cho '{assignment_name}'.")
            LogModel.write_log(
                session.SESSION.get_username(),
                f"{assigned_by_name} đã thêm hạn chót thành công cho '{assignment_name}' đối với '{assigned_to_name}'."
            )

        except ValueError as ve:
            # Handle validation errors
            self.display_error(f"Thêm hạn chót thất bại: {ve}")
            logging.error(f"Thêm hạn chót thất bại: {ve}")
            LogModel.write_log(
                session.SESSION.get_username(),
                f"{assigned_by_name} đã thêm hạn chót thất bại cho '{assignment_name}' đối với '{assigned_to_name}': {ve}"
            )

        except Exception as e:
            # Handle other exceptions
            self.display_error("Có lỗi xảy ra")
            logging.error(f"Có lỗi xảy ra: {e}")
            LogModel.write_log(
                f"{assigned_by_name} đã thêm hạn chót thất bại cho '{assignment_name}' đối với '{assigned_to_name}': {e}"
            )

    def display_success(self, message):
        success_box = CustomMessageBox("Success", message, QMessageBox.Icon.Information, "Đóng", self)
        success_box.exec()

    def display_error(self, message):
        error_box = CustomMessageBox("error", message, QMessageBox.Icon.Warning, "Thử lại", self)
        error_box.exec()

    def set_selected_item(self, item_name):
        self.selected_item = item_name
        print(f"Selected item for deadline: {self.selected_item}")  # Debug or use as needed
