import os
import shutil
import sys
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox
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

    def handle_add_file(self):
        """Handle adding a file to the root directory."""
        try:
            # Open file dialog to select a file
            file_path, _ = QFileDialog.getOpenFileName(self.view, "Select a File", "", "All Files (*)")
            if not file_path:
                return  # User canceled the dialog

            # Copy the file to the root directory
            file_name = Path(file_path).name
            target_path = self.model.root_path / file_name
            shutil.copy(file_path, target_path)

            # Refresh the view
            root_index = self.model.index(str(self.model.root_path))
            self.view.update_tree_view(root_index)

            # Notify the view about the success
            self.view.display_success(f"File '{file_name}' added to {self.model.root_path}.")
        except Exception as e:
            # Notify the view about the failure
            self.view.display_error(f"Failed to add file: {e}")

    def handle_remove_file(self):
        """Handle removing a selected file from the file system."""
        try:
            # Get the selected file index
            selected_indexes = self.view.treeView.selectedIndexes()

            if not selected_indexes:
                self.view.display_error("No file selected.")
                return

            # Get the file path of the selected item
            index = selected_indexes[0]
            file_path = self.view.treeView.model().filePath(index)

            if not file_path:
                self.view.display_error("Could not retrieve the file path.")
                return

            # Initialize reply and ask for confirmation
            reply = QMessageBox.StandardButton.No  # Default value in case QMessageBox fails
            try:
                reply = QMessageBox.question(
                    self.view,
                    "Confirm Removal",
                    f"Are you sure you want to remove {file_path}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
            except Exception as e:
                self.view.display_error(f"Failed to display confirmation dialog: {e}")
                return

            # Proceed based on user's choice
            if reply == QMessageBox.StandardButton.Yes:
                # Remove the file
                self.remove_file_from_directory(file_path)

                # Notify success
                self.view.display_success(f"File '{file_path}' has been removed.")

                # Refresh the tree view
                self.view.refresh_tree_view()
            else:
                self.view.display_error("File removal cancelled.")

        except Exception as e:
            self.view.display_error(f"Failed to remove file: {e}")

    def remove_file_from_directory(self, file_path):
        """Remove the specified file from the directory."""
        if os.path.exists(file_path):
            try:
                os.remove(file_path)  # Remove the file
            except Exception as e:
                raise Exception(f"Error removing file: {e}")
        else:
            raise Exception("File not found.")

    def open_file(self, index):
        # Get the file path from the selected index
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
        """Add a new folder to the selected directory."""
        folder_name, _ = QFileDialog.getSaveFileName(self.view, "New Folder Name", "", "Folder (*)")
        if folder_name:
            try:
                # Create the folder
                os.makedirs(folder_name)
                self.view.display_success(f"Folder '{folder_name}' created.")

                # Refresh the view to show the new folder
                self.view.refresh_tree_view()
            except Exception as e:
                self.view.display_error(f"Failed to create folder: {e}")

    def handle_remove_folder(self):
        """Remove the selected folder."""
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