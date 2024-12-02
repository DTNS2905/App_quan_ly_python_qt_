from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTreeView

from configs import FILES_ROOT_PATH
from messages.contants import HEADERS_FILE_TREE


class FileTreeModel(QFileSystemModel):
    def __init__(self):
        super().__init__()  # Initialize parent class
        self.root_path = FILES_ROOT_PATH
        self.setRootPath(str(self.root_path))  # Directly set in the current instance
        self.custom_headers = HEADERS_FILE_TREE

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        """Override to provide custom headers."""
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            if section < len(self.custom_headers):
                return self.custom_headers[section]  # Return custom header
        return super().headerData(section, orientation, role)  # Fallback to default behavior

    def get_model(self):
        """Returns the file system model (self)."""
        return self

    def get_index(self, path):
        """Returns the QModelIndex for a given path."""
        return self.index(path)