from PyQt6 import uic, QtWidgets
from presenters.profile import ProfilePresenter


class LogDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/log.ui', self)
        self.presenter = ProfilePresenter(self)
