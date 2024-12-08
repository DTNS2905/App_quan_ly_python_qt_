from PyQt6 import uic, QtWidgets
from PyQt6.QtCore import QStringListModel, Qt
from PyQt6.QtWidgets import QMessageBox, QCompleter

from common import session
from configs import PERMISSION_PATH
from messages.messages import PERMISSION_DENIED
from messages.permissions import PERMISSION_GRANT, PERMISSION_UNGRANT
from presenters.auth import AuthPresenter
from presenters.permission import PermissionPresenter
from ui_components.custom_messgae_box import CustomMessageBox


class PermissionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, action_type=None):
        super().__init__(parent)
        uic.loadUi(PERMISSION_PATH, self)
        self.setWindowTitle("Màn Hình Chỉnh Quyền")

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
            if original_permission.strip()
            and translated_permission.strip()  # Filter out empty strings
        }

        # Use the translated permissions for display
        translated_permissions = list(self.translation_map.keys())
        self.model = QStringListModel(translated_permissions)
        self.listView.setModel(self.model)

        user_assign = session.SESSION.get_username()

        def do_permission(
            action, _username: str, _permissions: list[str], _user_assgin: str
        ):
            permission = (
                PERMISSION_GRANT
                if action == "assign_permission"
                else PERMISSION_UNGRANT
            )
            if not session.SESSION.match_permissions(permission):
                self.display_error(f"{permission}: {PERMISSION_DENIED}")
                return

            if action == "assign_permission":
                self.presenter.assign_permissions_to_user(
                    _username, _permissions, _user_assgin
                )
            elif action == "unassign_permission":
                self.presenter.unassign_permissions_from_user(
                    _username, _permissions, _user_assgin
                )
            else:
                self.display_error(f"Hành động không rõ ràng")

        self.perform_button.clicked.connect(
            lambda: do_permission(
                action_type, self.lineEdit.text(), self.process_selection(), user_assign
            )
        )

        # Initialize QCompleter
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )  # Corrected: Use enum
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Match substrings
        self.completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )  # Use popup for suggestions

        # Set the model for the completer
        self.string_list_model = QStringListModel()  # Start with an empty model
        self.completer.setModel(self.string_list_model)

        # Attach the completer to the lineEdit
        self.lineEdit.setCompleter(self.completer)

        self.lineEdit.textChanged.connect(self.presenter.update_suggestions)

    def process_selection(self):
        """Retrieve original permissions from selected translated ones."""
        # Retrieve selected indexes
        selected_indexes = self.listView.selectionModel().selectedIndexes()
        selected_translations = [self.model.data(index) for index in selected_indexes]

        # Map back to original permissions
        selected_originals = [
            (
                ", ".join(self.translation_map[translation])
                if isinstance(self.translation_map[translation], list)
                else self.translation_map[translation]
            )
            for translation in selected_translations
        ]
        return selected_originals if selected_originals else None

    def display_success(self, message):
        """Display a custom success message."""
        success_box = CustomMessageBox(
            "Thành công", message, QMessageBox.Icon.Information, "Đóng", self
        )
        success_box.exec()

    def display_error(self, message):
        """Display a custom error message."""
        error_box = CustomMessageBox(
            "Lỗi", message, QMessageBox.Icon.Warning, "Đóng", self
        )
        error_box.exec()
