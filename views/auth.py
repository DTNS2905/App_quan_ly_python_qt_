from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QLineEdit, QMessageBox

from common import session
from common.session import UserSession
from presenters.auth import AuthPresenter
from presenters.permission import PermissionPresenter
from ui_components.custom_messgae_box import CustomMessageBox


class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/login.ui', self)
        self.presenter = AuthPresenter(self)
        self.permission_presenter = PermissionPresenter(self)

        # Add default user
        self.presenter.add_default_user('admin', 'admin123')

        # Table widget
        # Add default permission
        self.permission_presenter.add_default_permissions()
        self.permission_presenter.assign_all_permissions("admin")

        # Connect login button
        @self.login.clicked.connect
        def handle_login():
            username, permissions = self.presenter.handle_login()
            session.SESSION = UserSession(username, permissions)

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

