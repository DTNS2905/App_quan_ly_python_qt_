import logging
import traceback

from PyQt6 import QtWidgets, uic

from configs import ITEM_PERMISSION_PATH
from presenters.permission import PermissionPresenter


class ItemPermissionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(ITEM_PERMISSION_PATH, self)
        self.presenter = PermissionPresenter(self)
        try:
            self.presenter.populate_item_table()
        except Exception:
            logging.error(traceback.print_exc())
