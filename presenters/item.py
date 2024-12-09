import logging
import os
import traceback

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QGraphicsDropShadowEffect,
    QDialog,
)

from common import session
from common.presenter import Presenter
from messages.messages import (
    PERMISSION_DENIED,
    ADD_FILE_SUCCESS,
    ADD_FILE_ERROR,
    SELECTED_FILE_ERROR,
    FILE_REMOVE_FAIL,
    FILE_REMOVE_SUCCESS,
    OPEN_FILE_FAIL,
    FOLDER_CREATE_ERROR,
    FOLDER_SELECTED_NOT_FOUND,
    FOLDER_CREATE_SUCCESS,
    FOLDER_REMOVE_SUCCESS,
    FOLDER_REMOVE_ERROR,
    FILE_NOT_FOUND,
)
from messages.permissions import (
    FILE_CREATE,
    FILE_DELETE,
    FILE_DOWNLOAD,
    FOLDER_CREATE,
    FOLDER_DELETE,
    FILE_RENAME,
    FOLDER_RENAME,
)
from models.item import ItemModel
from models.log import LogModel
from ui_components.cusom_input_dialog import CustomInputDialog


class ItemPresenter(Presenter):
    def __init__(self, view):
        super().__init__(view, ItemModel())

    def setup_view(self):
        """Set up the view with the file model."""
        self.view.set_model(self.model.get_model())

        # Customize tree view appearance
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(QPointF(3.0, 3.0))
        effect.setBlurRadius(25)
        effect.setColor(QColor("#111"))

        self.view.treeView.setGraphicsEffect(effect)
        self.view.treeView.setHeaderHidden(True)
        self.view.treeView.setAnimated(False)
        self.view.treeView.setIndentation(20)
        self.view.treeView.setSortingEnabled(True)
        self.view.treeView.expandAll()
        self.view.treeView.setColumnWidth(0, 300)  # Column 1 width
        self.view.treeView.setColumnWidth(2, 200)  # Column 1 width

        # Enable multi-selection in the QTreeView
        self.view.treeView.setSelectionMode(
            self.view.treeView.SelectionMode.ExtendedSelection
        )

        self.model.populate_data()

    def refresh_model(self):
        return self.model.refresh_model()

    def handle_add_files(self):
        """Handle adding multiple files to the root directory."""
        if not session.SESSION.match_permissions(FILE_CREATE):
            self.view.display_error(PERMISSION_DENIED)
            LogModel.write_log(
                session.SESSION.get_username(), f"{FILE_CREATE}: {PERMISSION_DENIED}"
            )
            return

        try:
            # Open file dialog to select multiple files
            file_paths, _ = QFileDialog.getOpenFileNames(
                self.view, "Chọn tài liệu", "", "Tất cả tài liệu(*)"
            )
            if not file_paths:
                return  # User canceled the dialog

            selected_index = self.view.treeView.currentIndex()
            model = self.view.treeView.model()
            parent_original_name = model.data(selected_index)

            for file_path in file_paths:
                username = session.SESSION.get_username()
                self.model.create_file(username, file_path, parent_original_name)

            # Notify the view about the success
            self.view.display_success(
                f"{', '.join(file_paths)} {ADD_FILE_SUCCESS} cho {self.model.get_root_path()}."
            )
            LogModel.write_log(
                session.SESSION.get_username(),
                f"{', '.join(file_paths)} {ADD_FILE_SUCCESS} cho {self.model.get_root_path()}.",
            )

            # Refresh the view
            self.view.refresh_tree_view()
        except Exception as e:
            # Notify the view about the failure
            self.view.display_error(f"{ADD_FILE_ERROR}: {e}")

    def handle_remove_files(self):
        """Handle removing multiple selected files from the file system using QTreeView."""

        can_all_remove = session.SESSION.match_permissions(FILE_DELETE)
        try:
            selected_indexes = self.view.treeView.selectedIndexes()
            selected_indexes = [
                value for index, value in enumerate(selected_indexes) if index % 4 == 0
            ]

            if not selected_indexes:
                self.view.display_error(SELECTED_FILE_ERROR)
                return

            # Collect unique file paths from selected indexes (to avoid duplicates)
            file_paths = set()
            model = self.view.treeView.model()
            not_deleted_files = set()
            for index in selected_indexes:
                original_name = model.data(index)
                if can_all_remove or session.SESSION.match_item_permissions(
                    original_name, FILE_DELETE
                ):
                    file_paths.add(original_name)
                else:
                    not_deleted_files.add(original_name)

            if len(not_deleted_files) > 0:
                self.view.display_error(
                    f"Xóa {', '.join(not_deleted_files)}: {PERMISSION_DENIED}"
                )

            if len(file_paths) > 0:
                # Confirmation dialog for batch file deletion
                reply = QMessageBox.question(
                    self.view,
                    "Xác nhận xóa",
                    f"Bạn chắc chắn muốn xóa {', '.join(file_paths)} ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    for file_path in file_paths:
                        try:
                            self.model.delete_file(file_path)  # Remove each file
                            LogModel.write_log(
                                session.SESSION.get_username(),
                                f" {FILE_REMOVE_SUCCESS} cho {file_path} ",
                            )
                        except Exception as e:
                            LogModel.write_log(
                                session.SESSION.get_username(),
                                f"{FILE_REMOVE_FAIL} cho {file_path}: {e}",
                            )
                            self.view.display_error(
                                f"{FILE_REMOVE_FAIL} cho '{file_path}': {e}"
                            )

                    self.view.display_success(
                        f" {FILE_REMOVE_SUCCESS} cho {', '.join(file_paths)} "
                    )

                    # Refresh the view after deletion
                    self.view.refresh_tree_view()
                else:
                    LogModel.write_log(session.SESSION.get_username(), FILE_REMOVE_FAIL)
                    self.view.display_error(FILE_REMOVE_FAIL)

        except Exception as e:
            LogModel.write_log(
                session.SESSION.get_username(), f"{FILE_REMOVE_FAIL}:{e}"
            )
            self.view.display_error(f"{FILE_REMOVE_FAIL}:{e}")

    def handle_download_item(self):
        # Replace this with your actual data bytes
        can_all_download = session.SESSION.match_permissions(FILE_DOWNLOAD)

        try:
            selected_index = self.view.treeView.currentIndex()
            model = self.view.treeView.model()
            original_name = model.data(selected_index)

            if not (
                can_all_download
                or session.SESSION.match_item_permissions(original_name, FILE_DOWNLOAD)
            ):
                self.view.display_error(f"Lưu {original_name}: {PERMISSION_DENIED}")
                LogModel.write_log(
                    session.SESSION.get_username(),
                    f"Lưu '{original_name}': {PERMISSION_DENIED}",
                )
                return

            data_bytes = self.model.get_file_bytes(original_name)
            if data_bytes is None:
                self.view.display_error(f"'{original_name}' không phải là tệp đơn")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self.view, "Lưu tệp", original_name, "All Files (*)"
            )
            if file_path:
                with open(file_path, "wb") as f:
                    f.write(data_bytes)
                self.view.display_success(
                    f"Lưu '{original_name}' về {file_path} thành công"
                )
        except Exception as e:
            self.view.display_error(f"Lưu thất bại: {str(e)}")
            logging.error(e)

    def handle_add_folder(self):
        """Thêm một thư mục mới vào thư mục đã chọn dưới đường dẫn gốc."""
        if not session.SESSION.match_permissions(FOLDER_CREATE):
            LogModel.write_log(session.SESSION.get_username(), PERMISSION_DENIED)
            self.view.display_error("Bạn không có quyền tạo thư mục.")  # Thông báo lỗi
            return

        try:
            # Use the custom dialog
            dialog = CustomInputDialog(
                self.view, "Thư mục mới", "Điền tên thư mục:", "Thêm", "Hủy"
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                folder_name = dialog.get_text()
                if not folder_name:
                    LogModel.write_log(
                        session.SESSION.get_username(), FOLDER_CREATE_ERROR
                    )
                    self.view.display_error(
                        "Tên thư mục không được để trống."
                    )  # Thông báo lỗi
                    return

                selected_index = self.view.treeView.currentIndex()
                model = self.view.treeView.model()
                parent_original_name = model.data(selected_index)

                username = session.SESSION.get_username()
                self.model.create_folder(username, folder_name, parent_original_name)

                LogModel.write_log(username, f"Thành công: Tạo thư mục '{folder_name}'")
                self.view.display_success(
                    f"Thư mục '{folder_name}' đã được tạo thành công."
                )  # Thông báo thành công

                # Refresh the view to show the new folder
                self.view.refresh_tree_view()
            else:
                LogModel.write_log(
                    session.SESSION.get_username(),
                    "Người dùng đã hủy việc tạo thư mục.",
                )  # Nhật ký khi hủy
        except Exception as e:
            self.view.display_error(f"Lỗi tạo thư mục: {e}")  # Thông báo lỗi hệ thống
            LogModel.write_log(session.SESSION.get_username(), f"Lỗi tạo thư mục: {e}")

    def handle_remove_folder(self):
        """Remove the selected folder."""
        can_all_remove = session.SESSION.match_permissions(FOLDER_DELETE)
        selected_indexes = self.view.treeView.selectedIndexes()
        if not selected_indexes:
            LogModel.write_log(
                session.SESSION.get_username(), FOLDER_SELECTED_NOT_FOUND
            )
            self.view.display_error(FOLDER_SELECTED_NOT_FOUND)
            return

        model = self.view.treeView.model()
        index = selected_indexes[0]
        original_name = model.data(index)
        folder_path = original_name

        if not (
            can_all_remove
            or session.SESSION.match_item_permissions(folder_path, FOLDER_DELETE)
        ):
            self.view.display_error(f"Xóa {folder_path}: {PERMISSION_DENIED}")
            LogModel.write_log(
                session.SESSION.get_username(),
                f"{FOLDER_REMOVE_ERROR}: {PERMISSION_DENIED}",
            )
            return

        reply = QMessageBox.question(
            self.view,
            "Xác nhận xóa",
            f"bạn chắc chắn muốn xóa thư mục ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Remove the folder
                self.model.delete_folder(folder_path)
                LogModel.write_log(
                    session.SESSION.get_username(),
                    f"{FOLDER_REMOVE_SUCCESS} cho '{folder_path}' .",
                )
                self.view.display_success(
                    f"{FOLDER_REMOVE_SUCCESS} cho '{folder_path}' ."
                )

                # Refresh the view to remove the deleted folder
                self.view.refresh_tree_view()
            except Exception as e:
                LogModel.write_log(
                    session.SESSION.get_username(), f"{FOLDER_REMOVE_ERROR}: {e}"
                )
                self.view.display_error(f"{FOLDER_REMOVE_ERROR}: {e}")

    def handle_rename_file(self):
        can_all_rename = session.SESSION.match_permissions(FILE_RENAME)
        selected_indexes = self.view.treeView.selectedIndexes()
        if not selected_indexes:
            LogModel.write_log(
                session.SESSION.get_username(), f"{FOLDER_SELECTED_NOT_FOUND}"
            )
            self.view.display_error(FOLDER_SELECTED_NOT_FOUND)
            return

        selected_indexes = [
            value for index, value in enumerate(selected_indexes) if index % 4 == 0
        ]

        model = self.view.treeView.model()
        index = selected_indexes
        if len(index) > 1:
            self.view.display_error("Chỉ cho phép chọn 1 tệp để cập nhật tên")
            return

        original_name = model.data(index[0])
        _, file_ext = os.path.splitext(original_name)
        if not file_ext:
            self.view.display_error("Đây không phải là tệp")
            return

        if not (
            can_all_rename
            or session.SESSION.match_item_permissions(original_name, FILE_RENAME)
        ):
            self.view.display_error(
                f"Cập nhật tên tệp {original_name}: {PERMISSION_DENIED}"
            )
            LogModel.write_log(
                session.SESSION.get_username(),
                f"Cập nhật tên tệp {original_name}: {PERMISSION_DENIED}",
            )
            return

        dialog = CustomInputDialog(
            self.view, "Sửa tên tệp", "Điền tên tệp:", "Cập nhật"
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_root_name = dialog.get_text()
            if not new_root_name:
                LogModel.write_log(
                    session.SESSION.get_username(), "Tên tệp không được để trống."
                )
                self.view.display_error("Tên tệp không được để trống.")
                return

            new_name = new_root_name + "." + file_ext
            try:
                self.model.rename_item(original_name.strip(), new_name.strip())
            except Exception as e:
                self.view.display_error(f"Cập nhật tên tệp {original_name}: {str(e)}")

    def handle_rename_folder(self):
        can_all_rename = session.SESSION.match_permissions(FOLDER_RENAME)
        selected_indexes = self.view.treeView.selectedIndexes()
        if not selected_indexes:
            LogModel.write_log(
                session.SESSION.get_username(), f"{FOLDER_SELECTED_NOT_FOUND}"
            )
            self.view.display_error(FOLDER_SELECTED_NOT_FOUND)
            return

        selected_indexes = [
            value for index, value in enumerate(selected_indexes) if index % 4 == 0
        ]

        model = self.view.treeView.model()
        index = selected_indexes
        if len(index) > 1:
            self.view.display_error("Chỉ cho phép chọn 1 thư mục để cập nhật tên")
            return

        original_name = model.data(index[0])
        _, file_ext = os.path.splitext(original_name)
        if file_ext:
            self.view.display_error("Đây không phải là thư mục")
            return

        if not (
            can_all_rename
            or session.SESSION.match_item_permissions(original_name, FOLDER_RENAME)
        ):
            self.view.display_error(
                f"Cập nhật tên thư mục {original_name}: {PERMISSION_DENIED}"
            )
            LogModel.write_log(
                session.SESSION.get_username(),
                f"Cập nhật tên thư mục {original_name}: {PERMISSION_DENIED}",
            )
            return

        dialog = CustomInputDialog(
            self.view, "Sửa tên thư mục", "Điền tên thư mục:", "Cập nhật"
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.get_text()
            if not new_name:
                LogModel.write_log(
                    session.SESSION.get_username(), "Tên tệp không được để trống."
                )
                self.view.display_error("Tên thư mục không được để trống.")
                return

            try:
                self.model.rename_item(original_name.strip(), new_name.strip())
            except Exception as e:
                self.view.display_error(
                    f"Cập nhật tên thư mục {original_name}: {str(e)}"
                )
