from PyQt6 import uic, QtWidgets


class PermissionDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/permission_dialog.ui', self)

