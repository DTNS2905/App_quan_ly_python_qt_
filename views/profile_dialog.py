from PyQt6 import uic, QtWidgets
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox, QLineEdit
from common import session
from presenters.profile import ProfilePresenter
from ui_components.custom_messgae_box import CustomMessageBox


class ProfileDialog(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/profile.ui', self)
        self.presenter = ProfilePresenter(self)

        username = session.SESSION.get_username()
        self.presenter.load_profile(username)

        # Connect button to profile creation or update
        self.change_profile_button.clicked.connect(lambda: self.presenter.create_or_update_profile(
            username,
            self.name_input.text(),
            self.operative_unit_input.text(),
            self.telephone_input.text()
        ))

    def display_success(self, message):
        """Display a custom success message."""
        success_box = CustomMessageBox("Thành công", message, QMessageBox.Icon.Information, "Đóng", self)
        success_box.exec()

    def display_error(self, message):
        """Display a custom error message."""
        error_box = CustomMessageBox("Lỗi", message, QMessageBox.Icon.Warning, "Đóng", self)
        error_box.exec()
