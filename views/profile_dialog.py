from PyQt6 import uic, QtWidgets

from presenters.profile import ProfilePresenter


class ProfileDialog(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/profile.ui', self)
        self.presenter = ProfilePresenter(self)

        self.presenter.load_profile("admin")

        self.change_profile_button.clicked.connect(self.presenter.create_or_update_profile)
