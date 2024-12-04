from PyQt6 import QtWidgets, uic


class RegisterDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/register_ui.ui', self)
