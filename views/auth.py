from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QLineEdit, QMessageBox

from common import session
from common.session import UserSession
from configs import LOGIN_UI_PATH
from models.log import LogModel
from presenters.auth import AuthPresenter
from presenters.permission import PermissionPresenter
from ui_components.custom_messgae_box import CustomMessageBox
from views.register_dialog import RegisterDialog


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.RegisterDialog = RegisterDialog(self)
        uic.loadUi(LOGIN_UI_PATH, self)
        self.setWindowTitle("Màn hình đăng nhập")
        self.presenter = AuthPresenter(self)
        self.permission_presenter = PermissionPresenter(self)
        self.log_model = LogModel()

        # Add default user
        self.presenter.add_default_user('admin', 'admin123')

        # Add default permission
        self.permission_presenter.add_default_permissions()
        self.permission_presenter.assign_all_permissions("admin")

        # Connect login button
        @self.login.clicked.connect
        def handle_login():
            result = self.presenter.handle_login()
            if result:  # Check if result is not None
                username, permissions = result
                session.SESSION = UserSession(username, permissions)
            else:
                # Log or handle login failure gracefully
                print("Login failed or user has no permissions.")

        # Initialize toggle button for password visibility
        self.password_visible = False
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.toggle_button.setIcon(QIcon(":/icons/icons/eye-off.svg"))
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_password_visibility)

        self.register_button.clicked.connect(self.open_register_dialog)

    def open_register_dialog(self):
        """Open the RegisterDialog."""
        self.RegisterDialog.show()  # Non-modal dialog
    def closeEvent(self, event):
        self.presenter.close()
        event.accept()

    def toggle_password_visibility(self):
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_button.setIcon(QIcon(":/icons/icons/eye-off.svg"))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_button.setIcon(QIcon(":/icons/icons/eye.svg"))
        self.password_visible = not self.password_visible

    def display_success(self, message):
        success_box = CustomMessageBox("Success", message, QMessageBox.Icon.Information, "Đóng", self)
        success_box.exec()

    def display_error(self, message):
        error_box = CustomMessageBox("error", message, QMessageBox.Icon.Warning, "Thử lại", self)
        error_box.exec()
