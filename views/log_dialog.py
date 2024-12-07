import logging
import traceback

from PyQt6 import uic, QtWidgets

from configs import LOG_UI_PATH
from presenters.log import LogPresenter


class LogDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(LOG_UI_PATH, self)
        self.presenter = LogPresenter(self)
        try:
            self.presenter.populate_table()
        except Exception:
            logging.error(traceback.print_exc())
        
