import logging
import traceback

from PyQt6 import uic, QtWidgets

from presenters.log import LogPresenter


class LogDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/log.ui', self)
        self.presenter = LogPresenter(self)
        try:
            self.presenter.populate_table()
        except Exception:
            logging.error(traceback.print_exc())
        
