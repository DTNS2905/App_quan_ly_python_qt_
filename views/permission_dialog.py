from PyQt6 import uic, QtWidgets
from PyQt6.QtCore import QStringListModel

from presenters.permission import PermissionPresenter


class PermissionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('ui/permission_dialog.ui', self)

        self.presenter = PermissionPresenter(self)
        self.user_presenter =

        permissions = self.presenter.fetch_user_permissions()
        permission_strings = [
            f"Permissions: {', '.join(dto.permissions)}"
            for dto in permissions
        ]

        self.model = QStringListModel(permission_strings)
        self.listView.setModel(self.model)

        self.perform_button.clicked.connect(lambda: self.presenter.assign_permission_to_user(
            self.lineEdit.text(),

        ))

    def process_selection(self):
        # Retrieve selected indexes
        selected_indexes = self.list_view.selectionModel().selectedIndexes()
        selected_items = [self.model.data(index) for index in selected_indexes]
        if selected_items:
            return f"{', '.join(selected_items)}"
        else:
            return

