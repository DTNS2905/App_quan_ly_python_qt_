from PyQt6 import QtWidgets

from common import session
from common.presenter import Presenter
from messages.contants import PERMISSION_TRANSLATIONS
from messages.messages import GRANT_PERMISSION_SUCCESSFULLY, PERMISSION_DENIED, PERMISSION_GRANTED

from models.permission import PermissionModel


class PermissionPresenter(Presenter):

    FILE_PERMISSIONS = [
        "file:view", "file:create", "file:update", "file:execute", "file:delete",
    ]

    FOLDER_PERMISSION = [
        "folder:view", "folder:create", "folder:update", "folder:delete",
    ]

    PERMISSION_PERMISSION = [
        "permission:view", "permission:create", "permission:update", "permission:grant", "permission:delete",
    ]

    ALL_PERMISSION = [*FILE_PERMISSIONS, *FOLDER_PERMISSION, *PERMISSION_PERMISSION]

    VIEW_SCOPES = [p for p in ALL_PERMISSION if ":view" in p]

    def __init__(self, view):
        super().__init__(view, PermissionModel())

    def assign_permission_to_user(self, username, permission):
        """Assign a permission to a user."""
        if not session.SESSION.match_permissions("permission:grant"):
            self.view.display_error(PERMISSION_DENIED)
            return

        try:
            self.model.assign_permission_to_user(username, permission)
            self.view.display_success(GRANT_PERMISSION_SUCCESSFULLY)
        except Exception as e:
            self.view.display_error(str(e))

    def translate_permissions(self, permissions: list[str]) -> list[str]:
        """Translate a list of permissions to Vietnamese."""
        return [PERMISSION_TRANSLATIONS.get(permission, permission) for permission in permissions]

    def populate_table(self):
        """Populate QTableWidget with user permissions data."""
        user_permissions = self.model.fetch_user_permissions()
        self.view.user_permission_table.setRowCount(0)  # Clear table

        for row, user_permission in enumerate(user_permissions):
            username = user_permission.username
            translated_permissions = self.translate_permissions(user_permission.permissions)
            permissions_text = " ; ".join(translated_permissions)
            self.view.user_permission_table.insertRow(row)
            self.view.user_permission_table.setItem(row, 0, QtWidgets.QTableWidgetItem(username))
            self.view.user_permission_table.setItem(row, 1, QtWidgets.QTableWidgetItem(" \n ".join(translated_permissions )))

        self.view.user_permission_table.resizeColumnsToContents()
        self.view.user_permission_table.resizeRowsToContents()

    def add_default_permissions(self):
        """Add default permissions."""
        default_permissions = self.ALL_PERMISSION
        for permission in default_permissions:
            try:
                self.model.add_permission(permission)
            except Exception as e:
                print(f"Failed to add permission '{permission}': {e}")

    def assign_all_permissions(self, username: str):
        default_permissions = self.ALL_PERMISSION
        for permission in default_permissions:
            try:
                self.model.assign_permission_to_user(username, permission)
            except Exception as e:
                print(f"Failed to assign permission '{permission}': {e}")
