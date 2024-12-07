from PyQt6.QtWidgets import QTableWidgetItem

from common import session
from common.presenter import Presenter
from messages.messages import PERMISSION_DENIED
from messages.permissions import LOG_VIEW
from models.log import LogModel, LogTableData


class LogPresenter(Presenter):

    def __init__(self, view):
        super().__init__(view, LogModel())

    def populate_table(self):
        if not session.SESSION.match_permissions(LOG_VIEW):
            self.view.display_error(PERMISSION_DENIED)
            LogModel.write_log(session.SESSION.get_username(), PERMISSION_DENIED)
            return

        logs: list[LogTableData] = self.model.fetch_table_log()
        self.view.tableWidget.setRowCount(0)

        for row, log in enumerate(logs):
            self.view.tableWidget.insertRow(row)
            self.view.tableWidget.setItem(row, 0, QTableWidgetItem(log.username))
            self.view.tableWidget.setItem(row, 1, QTableWidgetItem(log.message))
            self.view.tableWidget.setItem(row, 2, QTableWidgetItem(log.created_at))

        self.view.tableWidget.resizeColumnsToContents()
        self.view.tableWidget.resizeRowsToContents()
