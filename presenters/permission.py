from PyQt6 import QtWidgets

from common.presenter import Presenter

from models.permission import PermissionModel


class PermissionPresenter(Presenter):
    def __init__(self, view):
        super().__init__(view, PermissionModel())

    def handle_permission_check(self, username, permission):
        """Check if the user has the required permission and update the view."""
        if self.model.verify_permission(username, permission):
            self.view.display_success("Permission granted!")
        else:
            self.view.display_error("Permission denied! You do not have the required access.")

    def assign_permission_to_user(self, user_id, permission_id):
        """Assign a permission to a user."""
        try:
            self.model.assign_permission_to_user(user_id, permission_id)
            self.view.display_success("Permission assigned successfully!")
        except Exception as e:
            self.view.display_error(str(e))

    def populate_table(self):
        """Populate QTableWidget with user permissions data."""
        user_permissions = self.model.fetch_user_permissions()
        self.view.user_permission_table.setRowCount(0)  # Clear table

        for row, (username, permission) in enumerate(user_permissions):
            self.view.user_permission_table.insertRow(row)
            self.view.user_permission_table.setItem(row, 0, QtWidgets.QTableWidgetItem(username))
            self.view.user_permission_table.setItem(row, 1, QtWidgets.QTableWidgetItem(permission))

        self.view.user_permission_table.resizeColumnsToContents()