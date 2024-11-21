from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QMessageBox, QGraphicsDropShadowEffect

from presenters.file_tree import FileTreePresenter
import resources
from configs import FILES_ROOT_PATH


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('ui/admin_dashboard.ui', self)
        self.presenter = FileTreePresenter(self)

        self.home_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.stackedWidgetPage1))
        self.pushButton_4.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.stackedWidgetPage2))
        self.add_file_button.clicked.connect(self.presenter.handle_add_file)
        self.remove_file_button.clicked.connect(self.presenter.handle_remove_file)

        # Set treeView at FILES_ROOT_PATH
        self.presenter.setup_view()
        root_index = self.presenter.model.index(str(FILES_ROOT_PATH))  # Convert the path to QModelIndex
        self.treeView.setRootIndex(root_index)  # Set the root index for the tree view

        # Customize tree view appearance
        effect = QGraphicsDropShadowEffect()
        effect.setOffset(QPointF(3.0, 3.0))
        effect.setBlurRadius(25)
        effect.setColor(QColor("#111"))

        self.treeView.setGraphicsEffect(effect)
        self.treeView.setAnimated(False)
        self.treeView.setIndentation(20)
        self.treeView.setSortingEnabled(True)

    def set_model(self, model):
        self.treeView.setModel(model)

    def display_success(self, message):
        """Display a success message."""
        QMessageBox.information(self, "Success", message)

    def display_error(self, message):
        """Display an error message."""
        QMessageBox.critical(self, "Error", message)

    def update_tree_view(self, root_index):
        """Update the tree view to a specific root index."""
        self.treeView.setRootIndex(root_index)

    def refresh_tree_view(self):
        """Refresh the tree view to reflect any changes in the file system."""
        root_index = self.presenter.model.index(str(FILES_ROOT_PATH))
        self.treeView.setRootIndex(root_index)  # Reset the root index to refresh the view

