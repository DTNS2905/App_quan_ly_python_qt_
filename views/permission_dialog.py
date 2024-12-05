from PyQt6 import uic, QtWidgets
from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import QMessageBox

from common import session
from presenters.permission import PermissionPresenter
from ui_components.custom_messgae_box import CustomMessageBox


class PermissionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, action_type=None):
        super().__init__(parent)
        uic.loadUi('ui/permission_dialog.ui', self)

        self.action_type = action_type  # Store the action type ('assign' or 'unassign')

        self.presenter = PermissionPresenter(self)

        permissions = self.presenter.fetch_user_permissions()

        # Maintain a mapping of translated permissions to original permissions
        self.translation_map = {
            translated_permission: original_permission
            for dto in permissions
            for original_permission, translated_permission in zip(
                dto.permissions, self.presenter.translate_permissions(dto.permissions)
            )
        }

        # Use the translated permissions for display
        translated_permissions = list(self.translation_map.keys())
        self.model = QStringListModel(translated_permissions)
        self.listView.setModel(self.model)

        user_assign = session.SESSION.get_username()

        if action_type == "assign_permission":
            self.perform_button.clicked.connect(lambda: self.presenter.assign_permissions_to_user(
                self.lineEdit.text(),
                self.process_selection(),
                user_assign
            ))
        elif action_type == "assign_permission":
            self.perform_button.clicked.connect(lambda: self.presenter.unassign_permissions_from_user(
                self.lineEdit.text(),
                self.process_selection(),
                user_assign
            ))

    def process_selection(self):
        """Retrieve original permissions from selected translated ones."""
        # Retrieve selected indexes
        selected_indexes = self.listView.selectionModel().selectedIndexes()
        selected_translations = [self.model.data(index) for index in selected_indexes]

        # Map back to original permissions
        selected_originals = [
            ", ".join(self.translation_map[translation]) if isinstance(self.translation_map[translation], list)
            else self.translation_map[translation]
            for translation in selected_translations
        ]
        return selected_originals if selected_originals else None

    def display_success(self, message):
        """Display a custom success message."""
        success_box = CustomMessageBox("Thành công", message, QMessageBox.Icon.Information, "Đóng", self)
        success_box.exec()

    def display_error(self, message):
        """Display a custom error message."""
        error_box = CustomMessageBox("Lỗi", message, QMessageBox.Icon.Warning, "Đóng", self)
        error_box.exec()
