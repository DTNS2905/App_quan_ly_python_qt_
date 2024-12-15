import logging
import os
import sys
import traceback

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QInputDialog,
    QGraphicsDropShadowEffect,
    QDialog, QFileIconProvider,
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
    FOLDER_RENAME, FILE_VIEW,
)
from models.item import ItemModel, CustomItem
from models.log import LogModel
from ui_components.cusom_input_dialog import CustomInputDialog


class ItemPresenter(Presenter):
    def __init__(self, view):
        super().__init__(view, ItemModel())

    def setup_view(self):
        """Set up the view with the file model."""
        self.view.set_model(self.model.get_model())

        self.model.on_tree_expansion = self.expand_tree_view

        # Customize tree view appearance
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(QPointF(3.0, 3.0))
        effect.setBlurRadius(25)
        effect.setColor(QColor("#111"))

        self.view.treeView.setGraphicsEffect(effect)
        self.view.treeView.setHeaderHidden(False)
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
        """Handle adding multiple files to the selected directory."""
        if not session.SESSION.match_permissions(FILE_CREATE):
            self.view.display_error(PERMISSION_DENIED)
            LogModel.write_log(
                session.SESSION.get_username(), f"{FILE_CREATE}: {PERMISSION_DENIED}"
            )
            return

        try:
            # Open file dialog to select multiple files
            file_paths, _ = QFileDialog.getOpenFileNames(
                self.view, "Chọn tài liệu", "", "All Files (*)"
            )
            if not file_paths:
                return  # User canceled the dialog

            # Get the selected index from the tree view
            selected_index = self.view.treeView.currentIndex()
            parent_original_name = None

            if selected_index.isValid():
                # Validate the selected node
                model = self.view.treeView.model()
                parent_original_name = model.data(selected_index, Qt.ItemDataRole.DisplayRole)
                parent_node_type = model.data(selected_index, Qt.ItemDataRole.UserRole)

                if parent_node_type == "file":
                    # Files cannot act as parents
                    self.view.display_error("không thể thêm tài liệu")
                    LogModel.write_log(
                        session.SESSION.get_username(),
                        f"Lỗi không thể thêm các tài liệu dưới một tài liệu khác: {parent_original_name}",
                    )
                    return
            else:
                # If no valid node is selected, default to the root
                parent_original_name = None

            # Add each file
            username = session.SESSION.get_username()
            for file_path in file_paths:
                self.model.create_file(username, file_path, parent_original_name)

            # Notify the view about the success
            self.view.display_success(
                f"Tài liệu được thêm thành công {parent_original_name or 'root'}: {', '.join(file_paths)}."
            )
            LogModel.write_log(
                username,
                f"Các tài liệu được thêm {', '.join(file_paths)} tới {parent_original_name or 'root'}.",
            )

            # Refresh the tree view
            self.view.refresh_tree_view()

        except Exception as e:
            # Notify the view about the failure
            self.view.display_error(f"{ADD_FILE_ERROR}")
            logging.error(f"lỗi trong lúc thêm tài liệu: {e}")

    def handle_remove_files(self):
        """Handle removing multiple selected files from the file system using QTreeView."""
        can_all_remove = session.SESSION.match_permissions(FILE_DELETE)

        try:
            # Map all selected indexes to column 0 of their respective rows
            selected_indexes = list(
                {index.sibling(index.row(), 0) for index in self.view.treeView.selectedIndexes()}
            )

            if not selected_indexes:
                self.view.display_error(SELECTED_FILE_ERROR)
                return

            # Collect unique file paths from selected indexes
            file_paths = set()
            not_deleted_files = set()
            model = self.view.treeView.model()

            for index in selected_indexes:
                original_name = model.data(index)
                if can_all_remove or session.SESSION.match_item_permissions(
                        original_name, FILE_DELETE
                ):
                    file_paths.add(original_name)
                else:
                    not_deleted_files.add(original_name)

            # Display permission errors for files the user cannot delete
            if not_deleted_files:
                self.view.display_error(
                    f"Không thể xóa {', '.join(not_deleted_files)}: {PERMISSION_DENIED}"
                )

            if file_paths:
                # Confirmation dialog for batch file deletion
                reply = QMessageBox.question(
                    self.view,
                    "Xác nhận xóa",
                    f"Bạn chắc chắn muốn xóa {', '.join(file_paths)}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    for file_path in file_paths:
                        try:
                            # Remove each file
                            self.model.delete_file(file_path)
                            LogModel.write_log(
                                session.SESSION.get_username(),
                                f"{FILE_REMOVE_SUCCESS} cho {file_path}",
                            )
                        except Exception as e:
                            # Log and display error for failed deletions
                            LogModel.write_log(
                                session.SESSION.get_username(),
                                f"{FILE_REMOVE_FAIL} cho {file_path}: {e}",
                            )
                            self.view.display_error(
                                f"{FILE_REMOVE_FAIL} cho '{file_path}': {e}"
                            )

                    # Display success message for successfully deleted files
                    self.view.display_success(
                        f"{FILE_REMOVE_SUCCESS} cho {', '.join(file_paths)}"
                    )

                    # Refresh the view after deletion
                    self.view.refresh_tree_view()
                else:
                    LogModel.write_log(session.SESSION.get_username(), FILE_REMOVE_FAIL)
                    self.view.display_error(FILE_REMOVE_FAIL)

        except Exception as e:
            # Handle unexpected errors
            LogModel.write_log(
                session.SESSION.get_username(), f"{FILE_REMOVE_FAIL}: {e}"
            )
            self.view.display_error(f"{FILE_REMOVE_FAIL}")

    def handle_download_items(self):
        """
        Handles downloading of selected items in the tree view.
        Filters for unique rows and processes them.
        """

        # Check if the user has global download permissions
        can_all_download = session.SESSION.match_permissions(FILE_DOWNLOAD)

        try:
            # Retrieve selected indexes from the tree view
            selected_indexes = self.view.treeView.selectionModel().selectedIndexes()
            logging.info(f"Initial selected indexes: {selected_indexes}")

            # Filter only one index per selected row (first column)
            selected_rows = set()
            filtered_indexes = []
            for index in selected_indexes:
                if index.column() == 0:  # Process only the first column
                    if index.row() not in selected_rows:
                        selected_rows.add(index.row())
                        filtered_indexes.append(index)

            if not filtered_indexes:
                self.view.display_error("Không có tệp nào được chọn để tải xuống.")
                return

            logging.info(f"Filtered indexes (one per row): {filtered_indexes}")

            # Prompt the user to select a folder for saving the files
            folder_path = QFileDialog.getExistingDirectory(self.view, "Chọn thư mục để lưu tệp")
            if not folder_path:
                self.view.display_error("Thư mục lưu không được chọn.")
                return

            # Iterate over each selected file
            processed_files = set()
            successfully_downloaded_files = []  # Collect successful downloads
            for index in filtered_indexes:
                model = self.view.treeView.model()
                original_name = model.data(index)

                # Skip duplicates or invalid entries
                if not original_name or original_name in processed_files:
                    self.view.display_error(f"Bỏ qua những tài liệu không hợp lệ hoặc trùng tên : {original_name}")
                    logging.debug(f"Skipping invalid or duplicate item: {original_name}")
                    continue

                # Check permissions for each file
                if not (
                        can_all_download
                        or session.SESSION.match_item_permissions(original_name, FILE_DOWNLOAD)
                ):
                    error_message = f"Lưu '{original_name}': {PERMISSION_DENIED}"
                    self.view.display_error(error_message)
                    LogModel.write_log(
                        session.SESSION.get_username(),
                        error_message,
                    )
                    continue

                # Retrieve the file data
                data_bytes = self.model.get_file_bytes(original_name)
                if data_bytes is None:
                    self.view.display_error(f"'{original_name}' không phải là tệp đơn")
                    continue

                # Construct the file path
                file_path = os.path.join(folder_path, original_name)

                # Attempt to save the file
                try:
                    with open(file_path, "wb") as f:
                        f.write(data_bytes)
                    processed_files.add(original_name)
                    successfully_downloaded_files.append(original_name)
                    logging.info(f"Lưu '{original_name}' về {file_path} thành công")

                except Exception as write_error:
                    error_message = f"Lưu '{original_name}' thất bại: {str(write_error)}"
                    self.view.display_error(error_message)
                    logging.error(f"Error saving file '{original_name}': {write_error}")

            # Display a single success message with all downloaded files
            if successfully_downloaded_files:
                success_message = (
                        f"Các tệp sau đã được lưu thành công:\n"
                        + "\n".join(successfully_downloaded_files)
                )
                self.view.display_success(success_message)
                logging.info(success_message)

        except Exception as e:
            # Handle unexpected errors
            error_message = f"Lưu thất bại: {str(e)}"
            self.view.display_error(error_message)
            logging.error(f"Unexpected error during download: {e}")

    def handle_add_folder(self):
        """Thêm một thư mục mới vào thư mục đã chọn hoặc vào thư mục gốc nếu không có lựa chọn."""
        if not session.SESSION.match_permissions(FOLDER_CREATE):
            LogModel.write_log(session.SESSION.get_username(), PERMISSION_DENIED)
            self.view.display_error("Bạn không có quyền tạo thư mục.")  # Thông báo lỗi
            return

        try:
            # Get the selected index and model
            selected_index = self.view.treeView.currentIndex()
            model = self.view.treeView.model()

            # Check if the selected index is valid
            if selected_index.isValid():
                # Retrieve the selected item
                selected_item = model.itemFromIndex(selected_index)

                # Check if the selected item is a directory (using UserRole data)
                if selected_item.data(Qt.ItemDataRole.UserRole) != "directory":
                    self.view.display_error("Không thể thêm thư mục vào một tệp.")  # Thông báo lỗi
                    return

                # Use the selected folder as the parent node
                parent_original_name = selected_item.text()
            else:
                # Default to the root node if no valid selection
                parent_original_name = "root"
                if not parent_original_name:  # Ensure root node exists
                    self.view.display_error("Không thể xác định thư mục gốc.")  # Thông báo lỗi
                    return

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
                    self.view.display_error("Tên thư mục không được để trống.")  # Thông báo lỗi
                    return

                username = session.SESSION.get_username()
                LogModel.write_log(username, f"Thành công: Tạo thư mục '{folder_name}'")
                self.view.display_success(
                    f"Thư mục '{folder_name}' đã được tạo thành công."
                )  # Thông báo thành công

                self.model.create_folder(username, folder_name, parent_original_name)
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
        """Handle removing a single selected folder."""

        can_all_remove = session.SESSION.match_permissions(FOLDER_DELETE)

        # Map all selected indexes to column 0 of their respective rows
        selected_indexes = list(
            {index.sibling(index.row(), 0) for index in self.view.treeView.selectedIndexes()}
        )

        # Ensure only one folder is selected
        if not selected_indexes:
            LogModel.write_log(
                session.SESSION.get_username(), FOLDER_SELECTED_NOT_FOUND
            )
            self.view.display_error(FOLDER_SELECTED_NOT_FOUND)
            return

        if len(selected_indexes) > 1:
            self.view.display_error("Chỉ cho phép chọn 1 thư mục để xóa")
            return

        # Get the model and the selected index
        model = self.view.treeView.model()
        index = selected_indexes[0]  # Only one index is allowed

        # Get the folder name
        original_name = model.data(index)
        if not original_name:
            self.view.display_error("Không thể lấy thông tin của thư mục được chọn.")
            return

        folder_path = original_name

        # Check permissions
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

        # Confirmation dialog for folder deletion
        reply = QMessageBox.question(
            self.view,
            "Xác nhận xóa",
            f"Bạn chắc chắn muốn xóa thư mục '{folder_path}'?",
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

        # Map all selected indexes to column 0 of their respective rows
        selected_indexes = list(
            {index.sibling(index.row(), 0) for index in self.view.treeView.selectedIndexes()}
        )

        # Validate selection
        if not selected_indexes:
            LogModel.write_log(
                session.SESSION.get_username(), f"{FOLDER_SELECTED_NOT_FOUND}"
            )
            self.view.display_error(FOLDER_SELECTED_NOT_FOUND)
            return

        # Ensure only one item is selected
        if len(selected_indexes) > 1:
            self.view.display_error("Chỉ cho phép chọn 1 tệp để cập nhật tên")
            return

        # Get the model and the selected index
        model = self.view.treeView.model()
        index = selected_indexes[0]  # Only one index is allowed

        # Get the original name of the selected item
        original_name = model.data(index)
        if not original_name:
            self.view.display_error("Không thể lấy thông tin của mục được chọn.")
            return

        # Check if the selected item is a file
        _, file_ext = os.path.splitext(original_name)
        if not file_ext:
            self.view.display_error("Đây không phải là tệp")
            return

        # Check permissions
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

        # Show the rename dialog
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

            new_name = new_root_name + file_ext
            try:
                self.model.rename_item(original_name.strip(), new_name.strip())
                self.view.refresh_tree_view()
            except Exception as e:
                self.view.display_error(f"Không Cập nhật tên tệp {original_name}")

    def handle_rename_folder(self):
        can_all_rename = session.SESSION.match_permissions(FOLDER_RENAME)

        # Map all selected indexes to column 0 of their respective rows
        selected_indexes = list(
            {index.sibling(index.row(), 0) for index in self.view.treeView.selectedIndexes()}
        )

        # Validate selection
        if not selected_indexes:
            LogModel.write_log(
                session.SESSION.get_username(), f"{FOLDER_SELECTED_NOT_FOUND}"
            )
            self.view.display_error(FOLDER_SELECTED_NOT_FOUND)
            return

        # Ensure only one item is selected
        if len(selected_indexes) > 1:
            self.view.display_error("Chỉ cho phép chọn 1 thư mục để cập nhật tên")
            return

        # Get the model and the selected index
        model = self.view.treeView.model()
        index = selected_indexes[0]  # Only one index is allowed

        # Get the original name of the selected item
        original_name = model.data(index)
        if not original_name:
            self.view.display_error("Không thể lấy thông tin của mục được chọn.")
            return

        # Check if the selected item is a folder (no file extension)
        _, file_ext = os.path.splitext(original_name)
        if file_ext:
            self.view.display_error("Đây không phải là thư mục")
            return

        # Check permissions
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

        # Show the rename dialog
        dialog = CustomInputDialog(
            self.view, "Sửa tên thư mục", "Điền tên thư mục:", "Cập nhật"
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_name = dialog.get_text()
            if not new_name:
                LogModel.write_log(
                    session.SESSION.get_username(), "Tên thư mục không được để trống."
                )
                self.view.display_error("Tên thư mục không được để trống.")
                return

            try:
                self.model.rename_item(original_name.strip(), new_name.strip())
                self.view.refresh_tree_view()
            except Exception as e:
                self.view.display_error(
                    f"Cập nhật tên thư mục {original_name}"
                )

    def update_suggestions(self, text):
        """Fetch matching name of items from the database and update the completer's suggestions."""
        suggestions = []
        if not text.strip():
            # Clear suggestions if the input is empty
            self.view.string_list_model.setStringList(suggestions)
            return

        try:
            # Fetch suggestions from the database
            if not session.SESSION.match_permissions(FILE_VIEW):
                username = session.SESSION.get_username()
                suggestions = self.model.fetch_items_based_on_suggestions_and_permissions(text, username)
            else:
                suggestions = self.model.fetch_all_items_based_on_suggestions(text)

            self.view.string_list_model.setStringList(suggestions)
        except Exception as e:
            # Handle potential errors during database fetching
            logging.error(f" Không thể tìm gợi ý cho tài liệu hoặc thư mục - lỗi kỹ thuật: {e}")
            self.view.string_list_model.setStringList([])

    def search_tree(self, search_text: str):
        """
        Handle tree search logic and notify the view to update the display.
        """
        if not search_text.strip():
            self.clear_highlights()
            return

        matches = self.model.search_tree_iterative(search_text)
        self.view.expand_and_highlight(matches)

    def clear_highlights(self):
        self.model.clear_item_highlight()

    def expand_tree_view(self):
        self.view.treeView.expandAll()

    def open_file(self, original_name):
        try:
            # Fetch the file details from the model
            item_details = self.model.get_item_details(original_name)
            if not item_details:
                self.view.display_error(f"Không tìm thấy tệp: {original_name}")
                return

            item_id, code, file_type = item_details
            if file_type != "file":
                self.view.display_error(f"'{original_name}' không phải là tệp đơn")
                return

            # Construct the file path
            files_storage_path = self.model.get_path_for_files_storage()
            file_path = os.path.join(files_storage_path, code)

            # Open the file using platform-specific commands
            self._open_file_platform(file_path)

        except Exception as e:
            self.view.display_error(f"Lỗi khi mở tệp")

    def _open_file_platform(self, file_path):
        """
        Opens the file using the default application based on the platform.
        """
        if sys.platform.startswith("win32"):
            os.startfile(file_path)  # Windows
        elif sys.platform.startswith("darwin"):
            os.system(f'open "{file_path}"')  # macOS
        else:
            os.system(f'xdg-open "{file_path}"')  # Linux

    def get_model_for_view(self):
        return self.model.get_model()
