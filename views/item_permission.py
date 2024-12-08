from PyQt6 import QtWidgets, uic

from configs import ITEM_PERMISSION_PATH


class ItemPermissionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(ITEM_PERMISSION_PATH, self)

