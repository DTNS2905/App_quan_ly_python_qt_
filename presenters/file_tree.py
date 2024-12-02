import os
import shutil
import sys
from pathlib import Path

from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QInputDialog, QGraphicsDropShadowEffect, QHeaderView

from common import session
from common.presenter import Presenter
from messages.messages import PERMISSION_DENIED, ADD_FILE_SUCCESS, ADD_FILE_ERROR, SELECTED_FILE_ERROR, \
    FILE_REMOVE_FAIL, FILE_REMOVE_SUCCESS, OPEN_FILE_FAIL, FOLDER_SELECTED_FAIL, FOLDER_CREATE_ERROR, FOLDER_EXISTED, \
    FOLDER_SELECTED_NOT_FOUND, FOLDER_CREATE_SUCCESS, FOLDER_REMOVE_SUCCESS, FOLDER_REMOVE_ERROR, FILE_NOT_FOUND
from models.file_tree import FileTreeModel


class FileTreePresenter(Presenter):
    def __init__(self, view):
        super().__init__(view, FileTreeModel())

    def setup_view(self):
        """Set up the view with the file system model."""
        self.view.set_model(self.model.get_model())
        root_index = self.model.index(str(self.model.root_path))
        self.view.update_tree_view(root_index)
        # Customize tree view appearance
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(QPointF(3.0, 3.0))
        effect.setBlurRadius(25)
        effect.setColor(QColor("#111"))

        self.view.treeView.setGraphicsEffect(effect)
        self.view.treeView.setAnimated(False)
        self.view.treeView.setIndentation(20)
        self.view.treeView.setSortingEnabled(True)
        # self.set_custom_headers()

        header = self.view.treeView.header()
        # Stretch the first column
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        # Resize to contents for the second column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        # Resize to contents for the third column
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        # Resize to contents for the fourth column
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        # Enable multi-selection in the QTreeView
        self.view.treeView.setSelectionMode(self.view.treeView.SelectionMode.ExtendedSelection)

    def handle_add_files(self):
        """Handle adding multiple files to the root directory."""
        if not session.SESSION.match_permissions("file:create"):
            self.view.display_error(PERMISSION_DENIED)
            return

        try:
            # Open file dialog to select multiple files
            file_paths, _ = QFileDialog.getOpenFileNames(self.view, "Chọn tài liệu", "", "Tất cả tài liệu(*)")
            if not file_paths:
                return  # User canceled the dialog

            for file_path in file_paths:
                file_name = Path(file_path).name
                target_path = self.model.root_path / file_name

                # Copy the file to the root directory
                shutil.copy(file_path, target_path)

            # Refresh the view
            root_index = self.model.index(str(self.model.root_path))
            self.view.update_tree_view(root_index)

            # Notify the view about the success
            self.view.display_success(f"{len(file_paths)} {ADD_FILE_SUCCESS} cho {self.model.root_path}.")
        except Exception as e:
            # Notify the view about the failure
            self.view.display_error(f"{ADD_FILE_ERROR}: {e}")

    def handle_remove_files(self):
        """Handle removing multiple selected files from the file system using QTreeView."""
        if not session.SESSION.match_permissions("file:delete"):
            self.view.display_error(PERMISSION_DENIED)
            return

        try:
            selected_indexes = self.view.treeView.selectedIndexes()

            if not selected_indexes:
                self.view.display_error(SELECTED_FILE_ERROR)
                return

            # Collect unique file paths from selected indexes (to avoid duplicates)
            file_paths = set()
            for index in selected_indexes:
                file_path = self.view.treeView.model().filePath(index)
                if os.path.isfile(file_path):  # Only consider files, not directories
                    file_paths.add(file_path)

            if not file_paths:
                self.view.display_error(FILE_REMOVE_FAIL)
                return

            # Confirmation dialog for batch file deletion
            reply = QMessageBox.question(
                self.view,
                "Xác nhận xóa",
                f"Bạn chắc chắn muốn xóa {len(file_paths)} ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                for file_path in file_paths:
                    try:
                        os.remove(file_path)  # Remove each file
                    except Exception as e:
                        self.view.display_error(f"{FILE_REMOVE_FAIL} cho '{file_path}': {e}")

                self.view.display_success(f" {FILE_REMOVE_SUCCESS} cho {len(file_paths)} ")

                # Refresh the view after deletion
                self.view.refresh_tree_view()
            else:
                self.view.display_error(FILE_REMOVE_FAIL)

        except Exception as e:
            self.view.display_error(f"{FILE_REMOVE_FAIL}:{e}")

    def remove_file_from_directory(self, file_path):
        """Remove the specified file from the directory."""
        if not session.SESSION.match_permissions("file:delete"):
            self.view.display_error(PERMISSION_DENIED)
            return

        if os.path.exists(file_path):
            try:
                os.remove(file_path)  # Remove the file
            except Exception as e:
                raise Exception(f"{FILE_REMOVE_FAIL}: {e}")
        else:
            raise Exception(FILE_NOT_FOUND)

    def open_file(self, index):
        # Get the file path from the selected index
        if not session.SESSION.match_permissions("file:execute"):
            self.view.display_error(PERMISSION_DENIED)
            return

        file_path = self.model.get_model().filePath(index)

        if os.path.isfile(file_path):
            try:
                # Open the file using the default application based on the platform
                if sys.platform.startswith("win32"):
                    os.startfile(file_path)  # Windows
                elif sys.platform.startswith("darwin"):
                    os.system(f'Mở "{file_path}"')  # macOS
                else:
                    os.system(f'mở "{file_path}"')  # Linux
            except Exception as e:
                print(f"{OPEN_FILE_FAIL}: {e}")
        else:
            print(FOLDER_SELECTED_FAIL)

    def handle_add_folder(self):
        """Add a new folder to the selected directory under the root path."""
        if not session.SESSION.match_permissions("folder:create"):
            self.view.display_error(PERMISSION_DENIED)
            return

        try:
            # Prompt for the folder name instead of path
            folder_name, ok = QInputDialog.getText(self.view, "Thư mục mới", " Điền tên thư mục:")
            if not ok or not folder_name.strip():
                self.view.display_error(FOLDER_CREATE_ERROR)
                return

            # Ensure it's being created under the root path
            target_path = self.model.root_path / folder_name.strip()

            # Check if the folder already exists
            if target_path.exists():
                self.view.display_error(f"{FOLDER_EXISTED} '{target_path}'")
                return

            # Create the folder
            os.makedirs(target_path)
            self.view.display_success(f"{FOLDER_CREATE_SUCCESS}:'{target_path}'")

            # Refresh the view to show the new folder
            self.view.refresh_tree_view()
        except Exception as e:
            self.view.display_error(f"{FOLDER_CREATE_ERROR}:{e}")

    def handle_remove_folder(self):
        """Remove the selected folder."""
        if not session.SESSION.match_permissions("folder:delete"):
            self.view.display_error(PERMISSION_DENIED)
            return

        selected_indexes = self.view.treeView.selectedIndexes()
        if not selected_indexes:
            self.view.display_error(FOLDER_SELECTED_NOT_FOUND)
            return

        index = selected_indexes[0]
        folder_path = self.view.treeView.model().filePath(index)

        if os.path.isdir(folder_path):
            reply = QMessageBox.question(
                self.view,
                "Xác nhận xóa",
                f"Bạn chắc chắn muốn xóa thư mục '{folder_path}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # Remove the folder
                    os.rmdir(folder_path)
                    self.view.display_success(f"{FOLDER_REMOVE_SUCCESS} cho '{folder_path}' .")

                    # Refresh the view to remove the deleted folder
                    self.view.refresh_tree_view()
                except Exception as e:
                    self.view.display_error(f"{FOLDER_REMOVE_ERROR}: {e}")
        else:
            self.view.display_error(FOLDER_SELECTED_FAIL)

    # def set_custom_headers(self):
    #     """Set custom headers for the file system model."""
    #     for i, header_text in enumerate(self.model.custom_headers):
    #         # Call setHeaderData correctly on the model
    #         self.model.setHeaderData(i, Qt.Orientation.Horizontal, header_text)  # Correct way to call
