import bcrypt

from common.auth import verify_password
from common.presenter import Presenter
from models.auth import AuthModel
from PyQt5 import QtWidgets


class AuthPresenter(Presenter):
    def __init__(self, view):
        super().__init__(view, AuthModel())
        self._verify_password = verify_password

    def handle_login(self):
        username = self.view.username_input.text()
        password = self.view.password_input.text()

        hashed_password = self.model.verify_user(username)
        if hashed_password and self._verify_password(password, hashed_password):
            QtWidgets.QMessageBox.information(self.view, "Login Successful", "Welcome!")
            self.view.accept()  # Close dialog and signal success
        else:
            QtWidgets.QMessageBox.warning(self.view, "Login Failed", "Invalid username or password.")

    def add_default_user(self, username, password):
        self.model.add_user(username, password)
