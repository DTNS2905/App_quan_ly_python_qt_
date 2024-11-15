import bcrypt
from models.auth_model import AuthModel
from PyQt5 import QtWidgets


class AuthPresenter:
    def __init__(self, view):
        self.view = view
        self.model = AuthModel()

    def handle_login(self):
        username = self.view.username_input.text()
        password = self.view.password_input.text()

        hashed_password = self.model.verify_user(username)
        if hashed_password and bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            QtWidgets.QMessageBox.information(self.view, "Login Successful", "Welcome!")
            self.view.accept()  # Close dialog and signal success
        else:
            QtWidgets.QMessageBox.warning(self.view, "Login Failed", "Invalid username or password.")

    def add_default_user(self, username, password):
        self.model.add_user(username, password)

    def close(self):
        self.model.close_connection()
