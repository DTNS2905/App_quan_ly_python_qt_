from PyQt6.QtWidgets import QTableWidgetItem

from common.presenter import Presenter
from models.log import LogModel, LogTableData


class LogPresenter(Presenter):

    def __init__(self, view):
        super().__init__(view, LogModel())

    def populate_table(self):
        logs: list[LogTableData] = self.model.fetch_table_log()
        self.view.tableWidget.setRowCount(0)

        for row, log in enumerate(logs):
            self.view.tableWidget.insertRow(row)
            self.view.tableWidget.setItem(row, 0, QTableWidgetItem(log.username))
            self.view.tableWidget.setItem(row, 1, QTableWidgetItem(log.message))
            self.view.tableWidget.setItem(row, 2, QTableWidgetItem(log.created_at))

        self.view.tableWidget.resizeColumnsToContents()
        self.view.tableWidget.resizeRowsToContents()
