from PyQt6.QtGui import QFileSystemModel
from configs import FILES_ROOT_PATH


class FileTreeModel:
    def __init__(self):
        self.root_path = FILES_ROOT_PATH
        self.model = QFileSystemModel()
        self.model.setRootPath(str(self.root_path))

    def get_model(self):
        """Returns the file system model."""
        return self.model

    def index(self, path):
        """Returns the QModelIndex for a given path."""
        return self.model.index(path)
