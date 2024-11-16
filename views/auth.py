from PyQt5 import QtWidgets
from presenters.auth import AuthPresenter
from ui.authentication import Ui_Dialog


class LoginDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.presenter = AuthPresenter(self)

        # Add default user
        self.presenter.add_default_user('admin', 'admin123')

        # Connect login button
        self.login.clicked.connect(self.presenter.handle_login)

    def closeEvent(self, event):
        self.presenter.close()
        event.accept()
