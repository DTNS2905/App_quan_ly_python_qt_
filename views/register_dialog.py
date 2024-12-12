import logging
import traceback

from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox, QLineEdit

from configs import REGISTER_UI_PATH
from presenters.auth import AuthPresenter
from presenters.permission import PermissionPresenter
from ui_components.custom_messgae_box import CustomMessageBox


class RegisterDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(REGISTER_UI_PATH, self)

        self.presenter = AuthPresenter(self)
        self.permission_presenter = PermissionPresenter(self)

        # Connect register button to a handler
        self.register_button.clicked.connect(self.on_register_clicked)

        # Dictionary to map buttons to their corresponding fields
        self.toggle_mapping = {
            self.toggle_button: self.password_input,
            self.toggle_button_3: self.confirm_password_input,
        }

        # Initialize all password fields to hidden with eye-off icons
        for button, field in self.toggle_mapping.items():
            field.setEchoMode(QLineEdit.EchoMode.Password)
            button.setIcon(QIcon(":/icons/icons/eye-off.svg"))
            button.setCheckable(True)
            button.clicked.connect(self.toggle_password_visibility)

    def handle_register(self):
        """Handle the user registration logic."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        # Example validation logic
        if not username or not password:
            self.display_error("Tên đăng nhập và mật khẩu không được để trống.")
            return

        try:
            # Simulate calling a presenter or model to handle registration
            # Example: self.presenter.register_user(username, password)
            self.display_success(f"Đăng ký thành công! Chào mừng {username}.")
            self.close()  # Close the dialog after success
        except Exception as e:
            self.display_error(f"Đăng ký thất bại: {str(e)}")

    def display_success(self, message):
        """Display a custom success message."""
        success_box = CustomMessageBox(
            "Thành công", message, QMessageBox.Icon.Information, "Đóng", self
        )
        success_box.exec()

    def display_error(self, message):
        """Display a custom error message."""
        error_box = CustomMessageBox(
            "Lỗi", message, QMessageBox.Icon.Warning, "Đóng", self
        )
        error_box.exec()

    def on_register_clicked(self):
        """Handle the register button click."""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        is_admin = self.checkBox.isChecked()
        self.presenter.handle_register(username, password, confirm_password)
        if is_admin:
            try:
                self.permission_presenter.assign_some_permissions_as_admin(username)
                logging.info(f"Grant admin role to {username}")
            except:
                logging.error(traceback.print_exc())

    def toggle_password_visibility(self):
        """Toggle visibility for the appropriate password field."""
        button = self.sender()  # Identify which button was clicked
        field = self.toggle_mapping[button]  # Get the corresponding QLineEdit

        if button.isChecked():
            field.setEchoMode(QLineEdit.EchoMode.Normal)  # Show raw password
            button.setIcon(QIcon(":/icons/icons/eye.svg"))  # Show "eye open" icon
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)  # Show dots
            button.setIcon(QIcon(":/icons/icons/eye-off.svg"))  # Show "eye closed" icon
