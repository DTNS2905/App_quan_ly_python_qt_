import logging

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

        try:
            self.assignment_presenter.set_deadline(
                assignment_name, item_name, assigned_by_name, assigned_to_name,start_time,end_time
            )  # IDs can be hardcoded or dynamic
            self.display_success(f"hạn chót được thêm thành công cho '{assignment_name}'.")
            LogModel.write_log(
                f"{assigned_by_name} đã thêm hạn chótthành công cho '{assignment_name}' đối với '{assigned_by_name}"
            )
        except ValueError as ve:
            self.display_error("thêm hạn chót thất bại")
            logging.error(f"thêm hạn chót thất bại: {ve}")
            LogModel.write_log(
                f"{assigned_by_name} đã thêm hạn chót thất bại cho '{assignment_name}' đối với '{assigned_by_name}"
            )
        except Exception as e:
            self.display_error("có lỗi xảy ra")
            logging.error(f"có lỗi xảy ra: {e}")

    def display_success(self, message):
        success_box = CustomMessageBox("Success", message, QMessageBox.Icon.Information, "Đóng", self)
        success_box.exec()

    def display_error(self, message):
        error_box = CustomMessageBox("error", message, QMessageBox.Icon.Warning, "Thử lại", self)
        error_box.exec()

    def set_selected_item(self, item_name):
        self.selected_item = item_name
        print(f"Selected item for deadline: {self.selected_item}")  # Debug or use as needed
