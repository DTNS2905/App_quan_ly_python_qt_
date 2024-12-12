import logging
import traceback

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QPushButton, QMessageBox

from common import session
from common.presenter import Presenter
from messages.contants import PERMISSION_TRANSLATIONS
from messages.messages import *
from messages.permissions import (
    ALL_PERMISSION,
    PERMISSION_GRANT,
    PERMISSION_UNGRANT,
    DEFAULT_PERMISSION,
    USER_DELETE, DEFAULT_TEMPORARY_ADMIN_PERMISSION,
)
from models.log import LogModel

from models.permission import PermissionModel


class PermissionPresenter(Presenter):

    def __init__(self, view):
        super().__init__(view, PermissionModel())

    def assign_permission_to_user(self, username, permission):
        """Assign a permission to a user."""
        if not session.SESSION.match_permissions(PERMISSION_GRANT):
            self.view.display_error(PERMISSION_DENIED)
            LogModel.write_log(session.SESSION.get_username(), PERMISSION_DENIED)
            return

        try:
            self.model.assign_permission_to_user(username, permission)
            self.view.display_success(GRANT_PERMISSION_SUCCESSFULLY)
            LogModel.write_log(
                session.SESSION.get_username(), GRANT_PERMISSION_SUCCESSFULLY
            )
        except Exception as e:
            self.view.display_error(GRANT_PERMISSION_ERROR)
            logging.error(e)
            LogModel.write_log(session.SESSION.get_username(), str(e))

    def translate_permissions(self, permissions: list[str]) -> list[str]:
        """Translate a list of permissions to Vietnamese."""
        return [
            PERMISSION_TRANSLATIONS.get(permission, permission)
            for permission in permissions
        ]

    def populate_table(self):
        """Populate QTableWidget with user permissions data."""
        user_permissions = self.model.fetch_user_permissions()
        self.view.user_permission_table.setRowCount(0)  # Clear table

        for row, user_permission in enumerate(user_permissions):
            try:
                username = user_permission.username
                fullname = user_permission.fullname
                position = user_permission.position
                phone_number = user_permission.phone_number
                translated_permissions = self.translate_permissions(
                    user_permission.permissions
                )
                self.view.user_permission_table.insertRow(row)
                self.view.user_permission_table.setItem(
                    row, 0, QtWidgets.QTableWidgetItem(username)
                )
                self.view.user_permission_table.setItem(
                    row, 1, QtWidgets.QTableWidgetItem(fullname)
                )
                self.view.user_permission_table.setItem(
                    row, 2, QtWidgets.QTableWidgetItem(position)
                )
                self.view.user_permission_table.setItem(
                    row, 3, QtWidgets.QTableWidgetItem(phone_number)
                )
                self.view.user_permission_table.setItem(
                    row,
                    4,
                    QtWidgets.QTableWidgetItem(" \n ".join(translated_permissions)),
                )
                delete_button = QPushButton("Xóa")

                def delete_user(r):
                    if not session.SESSION.match_permissions(USER_DELETE):
                        self.view.display_error(PERMISSION_DENIED)
                        LogModel.write_log(
                            session.SESSION.get_username(), PERMISSION_DENIED
                        )
                        return

                    try:
                        index = self.view.user_permission_table.model().index(r, 0)
                        delete_username = self.view.user_permission_table.model().data(
                            index
                        )
                        reply = QMessageBox.question(
                            self.view,
                            "Xác nhận xóa",
                            f"bạn chắc chắn muốn xóa người dùng {delete_username} ?",
                            QMessageBox.StandardButton.Yes
                            | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No,
                        )
                        if reply == QMessageBox.StandardButton.Yes:
                            self.model.delete_user_by_username(delete_username)
                            self.view.display_success(
                                f"Xóa người dùng {delete_username}' thành công!."
                            )
                            self.populate_table()
                    except Exception as e:
                        logging.error(e)

                delete_button.clicked.connect(lambda checked, r=row: delete_user(r))

                self.view.user_permission_table.setIndexWidget(
                    self.view.user_permission_table.model().index(row, 5), delete_button
                )
            except Exception as e:
                logging.error(e)

        self.view.user_permission_table.resizeColumnsToContents()
        self.view.user_permission_table.resizeRowsToContents()

    def populate_item_table(self):
        user_permissions = self.model.fetch_user_item_permissions()
        self.view.item_permission_table.setRowCount(0)  # Clear table
        print(user_permissions)

        for row, user_permission in enumerate(user_permissions):
            try:
                username = user_permission.username
                item = user_permission.item
                translated_permissions = self.translate_permissions(
                    user_permission.permissions
                )
                self.view.item_permission_table.insertRow(row)
                self.view.item_permission_table.setItem(
                    row, 0, QtWidgets.QTableWidgetItem(username)
                )
                self.view.item_permission_table.setItem(
                    row, 1, QtWidgets.QTableWidgetItem(item)
                )
                self.view.item_permission_table.setItem(
                    row,
                    2,
                    QtWidgets.QTableWidgetItem(" \n ".join(translated_permissions)),
                )
            except Exception as e:
                logging.error(e)

        self.view.item_permission_table.resizeColumnsToContents()
        self.view.item_permission_table.resizeRowsToContents()

    def add_default_permissions(self):
        """Add default permissions."""
        default_permissions = ALL_PERMISSION
        for permission in default_permissions:
            try:
                self.model.add_permission(permission)
            except Exception as e:
                logging.error(f"Failed to add permission '{permission}': {e}")

    def assign_all_permissions(self, username: str):
        default_permissions = ALL_PERMISSION
        for permission in default_permissions:
            try:
                self.model.assign_permission_to_user(username, permission)
            except Exception as e:
                logging.error(f"Failed to assign permission '{permission}': {e}")

    def assign_some_permissions_as_admin(self, username: str):
        default_permissions = DEFAULT_TEMPORARY_ADMIN_PERMISSION
        for permission in default_permissions:
            try:
                self.model.assign_permission_to_user(username, permission)
            except Exception as e:
                logging.error(f"Failed to assign permission '{permission}': {e}")

    def assign_permissions_to_users_for_file(
            self, item_name: str, username: str, permissions: list[str]
    ) -> None:
        """
        Assign multiple permissions to a user for a specific file.

        :param item_name: The name of the file (original_name in the items table).
        :param username: The username to assign permissions to.
        :param permissions: List of permissions to assign.
        :raises ValueError: If any of the inputs are invalid or empty.
        :raises Exception: If the operation fails for any reason.
        """
        if not item_name:
            raise ValueError("Tên tệp không được để trống.")
        if not username:
            raise ValueError("Tên người dùng không được để trống")
        if not permissions or not all(isinstance(p, str) for p in permissions):
            raise ValueError("Danh sách quyền phải không rỗng và chứa các chuỗi hợp lệ.")

        try:
            logging.info(
                f"Đang gán các quyền {permissions} cho người dùng '{username}' đối với tài liệu hoặc thư mục '{item_name}'."
            )
            self.model.assign_permissions_to_users_for_file(item_name, username, permissions)
            logging.info(
                f"Đã gán quyền thành công cho người dùng '{username}' đối với tài liệu hoặc thư mục'{item_name}'."
            )
        except Exception as e:
            logging.error(
                f"Không thể gán quyền cho người dùng '{username}' đối với tài liệu hoặc thư mục '{item_name}': {e}"
            )
            raise

    def unassign_permissions_to_users_for_file(
            self, item_name: str, username: str, permissions: list[str]
    ):
        """
               Assign multiple permissions to a user for a specific file.

               :param item_name: The name of the file (original_name in the items table).
               :param username: The username to assign permissions to.
               :param permissions: List of permissions to assign.
               :raises ValueError: If any of the inputs are invalid or empty.
               :raises Exception: If the operation fails for any reason.
               """
        if not item_name:
            raise ValueError("Tên tệp không được để trống.")
        if not username:
            raise ValueError("Tên người dùng không được để trống.")
        if not permissions or not all(isinstance(p, str) for p in permissions):
            raise ValueError("Danh sách quyền phải không rỗng và chứa các chuỗi hợp lệ.")

        try:
            logging.info(
                f"Đang gán các quyền {permissions} cho người dùng '{username}' đối với tài liệu hoặc thư mục '{item_name}'."
            )
            self.model.unassign_permissions_to_users_for_file(item_name, username, permissions)
            logging.info(
                f"Đã gán quyền thành công cho người dùng '{username}' đối với tài liệu hoặc thư mục '{item_name}'."
            )
        except Exception as e:
            logging.error(
                f"Không thể gỡ quyền cho người dùng '{username}' đối với tài liệu hoặc thư mục '{item_name}': {e}"
            )
            raise

    def assign_permissions_to_user(
            self, username: str, permissions: list[str], user_assgin: str
    ):
        """
        Assign multiple permissions to a user.

        Args:
            username (str): The username to assign permissions to.
            permissions (list[str]): List of permissions to assign.
            user_assign (str): The user performing the assignment.
        """

        if not session.SESSION.match_permissions(PERMISSION_GRANT):
            # Display error and log permission denial
            self.view.display_error(PERMISSION_DENIED)
            LogModel.write_log(
                session.SESSION.get_username(),
                f"{PERMISSION_DENIED} - người thực hiện:{user_assgin}'.",
            )
            return

        failed_permissions = []
        success_permissions = []

        for permission in permissions:
            if len(permission) < 3:  # Ensure permission strings are valid
                translated_permission = self.translate_permissions([permission])[0]
                self.view.display_error(
                    f"Quyền không có trong cơ sở dữ liệu: '{translated_permission}'"
                )
                LogModel.write_log(
                    session.SESSION.get_username(),
                    f"Quyền không có trong cơ sở dữ liệu: '{translated_permission}'. Bỏ Qua.",
                )
                failed_permissions.append(translated_permission)
                continue

            try:
                # Attempt to assign the permission
                self.model.assign_permission_to_user(username, permission)
                success_permissions.append(permission)
            except Exception as e:
                # Handle failures for specific permissions
                translated_permission = self.translate_permissions([permission])[0]
                LogModel.write_log(
                    session.SESSION.get_username(),
                    f"{user_assgin} không thể gắn '{translated_permission}' cho '{username}': {str(e)}",
                )

        translated_success_permissions = self.translate_permissions(success_permissions)
        translated_failed_permissions = failed_permissions  # Already translated

        # Handle the outcome
        if failed_permissions:
            # Show both successes and failures if applicable
            if success_permissions:
                success_message = (
                    f"{user_assgin} gắn {', '.join(translated_success_permissions)} cho {username}"
                )
                self.view.display_success(success_message)
                LogModel.write_log(
                    session.SESSION.get_username(),
                    f"{user_assgin} gắn {', '.join(translated_success_permissions)} cho {username}",
                )

            error_message = (
                f"{user_assgin} không thể gắn {', '.join(translated_failed_permissions)}"
            )
            self.view.display_error(error_message)
        else:
            # All permissions were successfully assigned
            success_message = (
                f"{user_assgin} gắn tất cả quyền thành công '{username}': {', '.join(translated_success_permissions)}"
            )
            self.view.display_success(success_message)
            LogModel.write_log(
                session.SESSION.get_username(),
                f"{user_assgin} gắn quyền thành công cho '{username}': {', '.join(translated_success_permissions)}",
            )

    def unassign_permissions_from_user(
            self, username: str, permissions: list[str], user_unassign: str
    ):
        """
        Unassign multiple permissions from a user.

        Args:
            username (str): The username from whom to unassign permissions.
            permissions (list[str]): List of permissions to unassign.
            user_unassign (str): The user performing the unassignment.
        """
        is_allowed = session.SESSION.match_permissions(PERMISSION_UNGRANT)
        if username == "admin":
            is_allowed = False

        if not is_allowed:
            # Display error and log permission denial
            self.view.display_error(PERMISSION_DENIED)
            LogModel.write_log(
                session.SESSION.get_username(),
                f"{PERMISSION_DENIED} - người thực hiện: {user_unassign}.",
            )
            return

        failed_permissions = []
        success_permissions = []

        for permission in permissions:
            if len(permission) < 3:
                translated_permission = self.translate_permissions([permission])[0]
                self.view.display_error(
                    f"Quyền không có trong cơ sở dữ liệu: '{translated_permission}'"
                )
                LogModel.write_log(
                    session.SESSION.get_username(),
                    f"Quyền không có trong cơ sở dữ liệu: '{translated_permission}'. Bỏ Qua.",
                )
                failed_permissions.append(permission)
                continue

            try:
                # Attempt to unassign the permission
                self.model.unassign_permission_from_user(username, permission)
                success_permissions.append(permission)
            except Exception as e:
                translated_permission = self.translate_permissions([permission])[0]
                # Handle failures for specific permissions
                failed_permissions.append(permission)
                LogModel.write_log(
                    session.SESSION.get_username(),
                    f"{user_unassign} không thể gỡ '{translated_permission}' khỏi '{username}': {str(e)}",
                )

        translated_success_permissions = self.translate_permissions(success_permissions)
        translated_failed_permissions = failed_permissions  # Already translated

        # Handle the outcome
        if failed_permissions:
            if success_permissions:
                success_message = f"{user_unassign} gỡ {', '.join(translated_success_permissions)} khỏi {username} thành công."
                self.view.display_success(success_message)
                LogModel.write_log(
                    session.SESSION.get_username(),
                    f"{user_unassign} gỡ {', '.join(translated_success_permissions)} khỏi {username} thành công.",
                )

            error_message = f"{user_unassign} không thể gỡ {', '.join(translated_failed_permissions)} khỏi {username}."
            self.view.display_error(error_message)
        else:
            success_message = (
                f"{user_unassign} đã gỡ quyền {translated_success_permissions} khỏi '{username}' thành công."
            )
            self.view.display_success(success_message)
            LogModel.write_log(
                session.SESSION.get_username(),
                f"{user_unassign} đã gỡ tất cả quyền {translated_success_permissions} khỏi '{username}' thành công.",
            )

    def fetch_user_permissions(self):
        user_permissions = self.model.fetch_user_permissions()

        return user_permissions

    def update_suggestions(self, text):
        """Fetch matching usernames from the database and update the completer's suggestions."""
        if not text.strip():
            # Clear suggestions if the input is empty
            self.view.string_list_model.setStringList([])
            return

        try:
            # Fetch suggestions from the database
            suggestions = self.model.fetch_usernames_based_on_suggestions(text)

            # Update the completer's model with the fetched suggestions
            self.view.string_list_model.setStringList(suggestions)
        except Exception as e:
            # Handle potential errors during database fetching
            logging.error(f"Không thể tìm gợi ý cho người dùng - lỗi kỹ thuật: {e}")
            self.view.string_list_model.setStringList([])

    def add_default_permissions_for_register(self):
        """Add default permissions."""
        default_permissions = DEFAULT_PERMISSION
        for permission in default_permissions:
            try:
                self.model.add_permission(permission)
            except Exception as e:
                logging.error(f"Failed to add permission '{permission}': {e}")
