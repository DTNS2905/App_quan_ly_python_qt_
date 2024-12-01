from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLineEdit, QMessageBox

from presenters.auth import AuthPresenter
from ui.authentication import Ui_Dialog
import resources
from ui_components.custom_messgae_box import CustomMessageBox


class LoginDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/login.ui', self)
        self.presenter = AuthPresenter(self)

        # Add default user
        self.presenter.add_default_user('admin', 'admin123')

        # Connect login button
        self.login.clicked.connect(self.presenter.handle_login)

        # Initialize toggle button for password visibility
        self.password_visible = False  # Track visibility state
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.toggle_button.setIcon(QIcon(":/icons/icons/eye-off.svg"))
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_password_visibility)

    def closeEvent(self, event):
        self.presenter.close()
        event.accept()

    def toggle_password_visibility(self):
        if self.password_visible:
            # Hide password
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_button.setIcon(QIcon(":/icons/icons/eye-off.svg"))
        else:
            # Show password
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_button.setIcon(QIcon(":/icons/icons/eye.svg"))
        self.password_visible = not self.password_visible

    def display_success(self, message):
        """Display a custom success message."""
        success_box = CustomMessageBox("Success", message, QMessageBox.Icon.Information, "Đóng", self)
        success_box.exec()

    def display_error(self, message):
        """Display a custom error message."""
        error_box = CustomMessageBox("error", message, QMessageBox.Icon.Warning, "Thử lại", self)
        error_box.exec()
