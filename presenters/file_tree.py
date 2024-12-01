import os
import shutil
import sys
from pathlib import Path

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QInputDialog, QGraphicsDropShadowEffect

from common import session
from common.presenter import Presenter
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

        # Enable multi-selection in the QTreeView
        self.view.treeView.setSelectionMode(self.view.treeView.SelectionMode.ExtendedSelection)

    def handle_add_files(self):
        """Handle adding multiple files to the root directory."""
        if not session.SESSION.match_permissions("file:create"):
            self.view.display_error("Người dùng không có quyền tạo tệp. Vui lòng liên hệ admin")
            return

        try:
            # Open file dialog to select multiple files
            file_paths, _ = QFileDialog.getOpenFileNames(self.view, "Select Files", "", "All Files (*)")
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
            self.view.display_success(f"{len(file_paths)} files added to {self.model.root_path}.")
        except Exception as e:
            # Notify the view about the failure
            self.view.display_error(f"Failed to add files: {e}")

    def handle_remove_files(self):
        """Handle removing multiple selected files from the file system using QTreeView."""
        if not session.SESSION.match_permissions("file:delete"):
            self.view.display_error("Người dùng không có quyền xóa tệp. Vui lòng liên hệ admin")
            return

        try:
            selected_indexes = self.view.treeView.selectedIndexes()

            if not selected_indexes:
                self.view.display_error("No files or folders selected.")
                return

            # Collect unique file paths from selected indexes (to avoid duplicates)
            file_paths = set()
            for index in selected_indexes:
                file_path = self.view.treeView.model().filePath(index)
                if os.path.isfile(file_path):  # Only consider files, not directories
                    file_paths.add(file_path)

            if not file_paths:
                self.view.display_error("No valid files selected.")
                return

            # Confirmation dialog for batch file deletion
            reply = QMessageBox.question(
                self.view,
                "Confirm Removal",
                f"Are you sure you want to remove {len(file_paths)} files?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                for file_path in file_paths:
                    try:
                        os.remove(file_path)  # Remove each file
                    except Exception as e:
                        self.view.display_error(f"Error removing '{file_path}': {e}")

                self.view.display_success(f"Successfully removed {len(file_paths)} files.")

                # Refresh the view after deletion
                self.view.refresh_tree_view()
            else:
                self.view.display_error("File removal cancelled.")

        except Exception as e:
            self.view.display_error(f"Failed to remove files: {e}")

    def remove_file_from_directory(self, file_path):
        """Remove the specified file from the directory."""
        if not session.SESSION.match_permissions("file:delete"):
            self.view.display_error("PERMISSION_DENIED")
            return

        if os.path.exists(file_path):
            try:
                os.remove(file_path)  # Remove the file
            except Exception as e:
                raise Exception(f"Error removing file: {e}")
        else:
            raise Exception("File not found.")

    def open_file(self, index):
        # Get the file path from the selected index
        if not session.SESSION.match_permissions("file:execute"):
            self.view.display_error("Người dùng không có quyền chạy tệp. Vui lòng liên hệ admin")
            return

        file_path = self.model.get_model().filePath(index)

        if os.path.isfile(file_path):
            try:
                # Open the file using the default application based on the platform
                if sys.platform.startswith("win32"):
                    os.startfile(file_path)  # Windows
                elif sys.platform.startswith("darwin"):
                    os.system(f'open "{file_path}"')  # macOS
                else:
                    os.system(f'xdg-open "{file_path}"')  # Linux
            except Exception as e:
                print(f"Failed to open file: {e}")
        else:
            print("Selected item is not a file.")

    def handle_add_folder(self):
        """Add a new folder to the selected directory under the root path."""
        if not session.SESSION.match_permissions("folder:create"):
            self.view.display_error("Người dùng không có quyền chạy tệp. Vui lòng liên hệ admin")
            return

        try:
            # Prompt for the folder name instead of path
            folder_name, ok = QInputDialog.getText(self.view, "New Folder", "Enter folder name:")
            if not ok or not folder_name.strip():
                self.view.display_error("No folder name provided.")
                return

            # Ensure it's being created under the root path
            target_path = self.model.root_path / folder_name.strip()

            # Check if the folder already exists
            if target_path.exists():
                self.view.display_error(f"Folder '{target_path}' already exists.")
                return

            # Create the folder
            os.makedirs(target_path)
            self.view.display_success(f"Folder '{target_path}' created.")

            # Refresh the view to show the new folder
            self.view.refresh_tree_view()
        except Exception as e:
            self.view.display_error(f"Failed to create folder: {e}")

    def handle_remove_folder(self):
        """Remove the selected folder."""
        if not session.SESSION.match_permissions("folder:delete"):
            self.view.display_error("Người dùng không có quyền xóa. Vui lòng liên hệ admin")
            return

        selected_indexes = self.view.treeView.selectedIndexes()
        if not selected_indexes:
            self.view.display_error("No folder selected.")
            return

        index = selected_indexes[0]
        folder_path = self.view.treeView.model().filePath(index)

        if os.path.isdir(folder_path):
            reply = QMessageBox.question(
                self.view,
                "Confirm Removal",
                f"Are you sure you want to delete the folder '{folder_path}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # Remove the folder
                    os.rmdir(folder_path)
                    self.view.display_success(f"Folder '{folder_path}' removed.")

                    # Refresh the view to remove the deleted folder
                    self.view.refresh_tree_view()
                except Exception as e:
                    self.view.display_error(f"Failed to remove folder: {e}")
        else:
            self.view.display_error("Selected item is not a folder.")
