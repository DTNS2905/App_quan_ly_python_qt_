import traceback

from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QInputDialog, QGraphicsDropShadowEffect

from common import session
from common.presenter import Presenter
from messages.messages import PERMISSION_DENIED, ADD_FILE_SUCCESS, ADD_FILE_ERROR, SELECTED_FILE_ERROR, \
    FILE_REMOVE_FAIL, FILE_REMOVE_SUCCESS, OPEN_FILE_FAIL, FOLDER_SELECTED_FAIL, FOLDER_CREATE_ERROR, FOLDER_EXISTED, \
    FOLDER_SELECTED_NOT_FOUND, FOLDER_CREATE_SUCCESS, FOLDER_REMOVE_SUCCESS, FOLDER_REMOVE_ERROR, FILE_NOT_FOUND
from models.item import ItemModel
from models.log import LogModel


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
        self.view.treeView.setSelectionMode(self.view.treeView.SelectionMode.ExtendedSelection)

        self.model.populate_data()

    def refresh_model(self):
        return self.model.refresh_model()

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

            selected_index = self.view.treeView.currentIndex()
            model = self.view.treeView.model()
            parent_original_name = model.data(selected_index)

            for file_path in file_paths:
                username = session.SESSION.get_username()
                self.model.create_file(username, file_path, parent_original_name)

            # Notify the view about the success
            self.view.display_success(f"{len(file_paths)} {ADD_FILE_SUCCESS} cho {self.model.get_root_path()}.")

            # Refresh the view
            self.view.refresh_tree_view()
        except Exception as e:
            # Notify the view about the failure
            self.view.display_error(f"{ADD_FILE_ERROR}: {e}")

    def handle_remove_files(self):
        """Handle removing multiple selected files from the file system using QTreeView."""
        if not session.SESSION.match_permissions("file:delete"):
            self.view.display_error(PERMISSION_DENIED)
            LogModel.write_log(session.SESSION.get_username(), PERMISSION_DENIED)
            return

        try:
            selected_indexes = self.view.treeView.selectedIndexes()
            selected_indexes = [value for index, value in enumerate(selected_indexes) if index % 4 == 0]

            if not selected_indexes:
                self.view.display_error(SELECTED_FILE_ERROR)
                return

            # Collect unique file paths from selected indexes (to avoid duplicates)
            file_paths = set()
            model = self.view.treeView.model()
            for index in selected_indexes:
                original_name = model.data(index)
                file_paths.add(original_name)

            # Confirmation dialog for batch file deletion
            reply = QMessageBox.question(
                self.view,
                "Xác nhận xóa",
                f"Bạn chắc chắn muốn xóa {', '.join(file_paths)} ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                for file_path in file_paths:
                    try:
                        self.model.delete_file(file_path)  # Remove each file
                        LogModel.write_log(session.SESSION.get_username(), f" {FILE_REMOVE_SUCCESS} cho {file_path} ")
                    except Exception as e:
                        LogModel.write_log(session.SESSION.get_username(),
                                           f"{FILE_REMOVE_FAIL} cho {file_path}: {e}")
                        self.view.display_error(f"{FILE_REMOVE_FAIL} cho '{file_path}': {e}")

                self.view.display_success(f" {FILE_REMOVE_SUCCESS} cho {', '.join(file_paths)} ")

                # Refresh the view after deletion
                self.view.refresh_tree_view()
            else:
                LogModel.write_log(session.SESSION.get_username(), FILE_REMOVE_FAIL)
                self.view.display_error(FILE_REMOVE_FAIL)

        except Exception as e:
            LogModel.write_log(session.SESSION.get_username(), f"{FILE_REMOVE_FAIL}:{e}")
            self.view.display_error(f"{FILE_REMOVE_FAIL}:{e}")

    def open_file(self, index):
        # Get the file path from the selected index
        if not session.SESSION.match_permissions("file:execute"):
            self.view.display_error(PERMISSION_DENIED)
            LogModel.write_log(session.SESSION.get_username(), PERMISSION_DENIED)
            return

        model = self.view.treeView.model()
        original_name = model.data(index)

        try:
            self.model.open_file(original_name)
        except Exception as e:
            LogModel.write_log(session.SESSION.get_username(), f"{OPEN_FILE_FAIL}: {e}")
            self.view.display_error(f"{OPEN_FILE_FAIL}: {e}")

    def handle_download_item(self):
        # Replace this with your actual data bytes
        try:
            selected_index = self.view.treeView.currentIndex()
            model = self.view.treeView.model()
            original_name = model.data(selected_index)
            data_bytes = self.model.get_file_bytes(original_name)
            if data_bytes is None:
                self.view.display_error(f"'{original_name}' không phải là tệp đơn")
                return

            file_path, _ = QFileDialog.getSaveFileName(self.view, "Lưu tệp", original_name, "All Files (*)")
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(data_bytes)
                self.view.display_success(f"Lưu '{original_name}' về {file_path} thành công")
        except Exception:
            print(traceback.format_exc())

    def handle_add_folder(self):
        """Add a new folder to the selected directory under the root path."""
        if not session.SESSION.match_permissions("folder:create"):
            LogModel.write_log(session.SESSION.get_username(), PERMISSION_DENIED)
            self.view.display_error(PERMISSION_DENIED)
            return

        try:
            # Prompt for the folder name instead of path
            folder_name, ok = QInputDialog.getText(self.view, "Thư mục mới", " Điền tên thư mục:")
            if not ok or not folder_name.strip():
                LogModel.write_log(session.SESSION.get_username(), FOLDER_CREATE_ERROR)
                self.view.display_error(FOLDER_CREATE_ERROR)
                return

            # # Ensure it's being created under the root path
            # target_path = self.model.root_path / folder_name.strip()

            # # Check if the folder already exists
            # if target_path.exists():
            #     self.view.display_error(f"{FOLDER_EXISTED} '{target_path}'")
            #     return

            selected_index = self.view.treeView.currentIndex()
            model = self.view.treeView.model()
            parent_original_name = model.data(selected_index)

            username = session.SESSION.get_username()
            self.model.create_folder(username, folder_name.strip(), parent_original_name)

            LogModel.write_log(username, f"{FOLDER_CREATE_SUCCESS}:'{folder_name}'")
            self.view.display_success(f"{FOLDER_CREATE_SUCCESS}:'{folder_name}'")

            # Refresh the view to show the new folder
            self.view.refresh_tree_view()
        except Exception as e:
            self.view.display_error(f"{FOLDER_CREATE_ERROR}:{e}")
            LogModel.write_log(session.SESSION.get_username(), f"{FOLDER_CREATE_ERROR}:{e}")

    def handle_remove_folder(self):
        """Remove the selected folder."""
        if not session.SESSION.match_permissions("folder:delete"):
            self.view.display_error(PERMISSION_DENIED)
            LogModel.write_log(session.SESSION.get_username(), PERMISSION_DENIED)
            return

        selected_indexes = self.view.treeView.selectedIndexes()
        if not selected_indexes:
            LogModel.write_log(session.SESSION.get_username(), FOLDER_SELECTED_NOT_FOUND)
            self.view.display_error(FOLDER_SELECTED_NOT_FOUND)
            return

        model = self.view.treeView.model()
        index = selected_indexes[0]
        original_name = model.data(index)
        folder_path = original_name

        reply = QMessageBox.question(
            self.view,
            "Xác nhận xóa",
            f"bạn chắc chắn muốn xóa thư mục ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Remove the folder
                self.model.delete_folder(folder_path)
                LogModel.write_log(session.SESSION.get_username(), f"{FOLDER_REMOVE_SUCCESS} cho '{folder_path}' .")
                self.view.display_success(f"{FOLDER_REMOVE_SUCCESS} cho '{folder_path}' .")

                # Refresh the view to remove the deleted folder
                self.view.refresh_tree_view()
            except Exception as e:
                LogModel.write_log(session.SESSION.get_username(), f"{FOLDER_REMOVE_ERROR}: {e}")
                self.view.display_error(f"{FOLDER_REMOVE_ERROR}: {e}")

    # def get_item_id_by_name(self, item_name):
    #     if not session.SESSION.match_permissions("folder:delete"):
    #         self.view.display_error(PERMISSION_DENIED)
    #         LogModel.write_log(session.SESSION.get_username(), PERMISSION_DENIED)
    #         return
    #     try:
    #         self.model.get_item_id_by_name(item_name)
    #     except Exception as e:
    #         print(f"{FOLDER_GET_ERROR}: {e}")

