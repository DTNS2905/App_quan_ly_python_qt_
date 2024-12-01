from PyQt6 import QtWidgets, uic
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QMessageBox

from presenters.file_tree import FileTreePresenter
from presenters.permission import PermissionPresenter
from configs import FILES_ROOT_PATH
from ui_components.custom_messgae_box import CustomMessageBox


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Màn hình chính")
        uic.loadUi('ui/admin_dashboard.ui', self)
        self.tree_presenter = FileTreePresenter(self)
        self.permission_presenter = PermissionPresenter(self)
        self.permission_presenter.populate_table()

        # Connect buttons to slots
        self.home_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.stackedWidgetPage1))
        self.manage_user_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.stackedWidgetPage2))

        self.home_button.clicked.connect(self.update_label_text)
        self.manage_user_button.clicked.connect(self.update_label_text)

        self.home_button.clicked.connect(self.change_button_style_on_click)
        self.manage_user_button.clicked.connect(self.change_button_style_on_click)

        self.add_file_button.clicked.connect(self.tree_presenter.handle_add_files)
        self.remove_file_button.clicked.connect(self.tree_presenter.handle_remove_files)

        self.add_folder_button.clicked.connect(self.tree_presenter.handle_add_folder)
        self.remove_folder_button.clicked.connect(self.tree_presenter.handle_remove_folder)

        # self.add_permission_button.clicked.connect()
        # self.remove_permission_button.clicked.connect()

        # Set up treeView at FILES_ROOT_PATH
        self.tree_presenter.setup_view()
        root_index = self.tree_presenter.model.index(str(FILES_ROOT_PATH))  # Convert the path to QModelIndex
        self.treeView.setRootIndex(root_index)  # Set the root index for the tree view
        # Execute files at FILES_ROOT_PATH
        self.treeView.doubleClicked.connect(self.tree_presenter.open_file)

        # Add Ctrl+A shortcut for Select All in treeView
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self.treeView)
        select_all_shortcut.activated.connect(self.select_all_items)

    def set_model(self, model):
        self.treeView.setModel(model)

    def display_success(self, message):
        """Display a custom success message."""
        success_box = CustomMessageBox("Success", message, QMessageBox.Icon.Information, "Đóng", self)
        success_box.exec()

    def display_error(self, message):
        """Display a custom error message."""
        error_box = CustomMessageBox("error", message, QMessageBox.Icon.Warning, "Đóng", self)
        error_box.exec()

    def update_tree_view(self, root_index):
        """Update the tree view to a specific root index."""
        self.treeView.setRootIndex(root_index)

    def refresh_tree_view(self):
        """Refresh the tree view to reflect any changes in the file system."""
        root_index = self.tree_presenter.model.index(str(FILES_ROOT_PATH))
        self.treeView.setRootIndex(root_index)  # Reset the root index to refresh the view

    def update_label_text(self):
        sender = self.sender()  # Get the button that triggered this slot
        # Update label based on the button's current text
        if sender.objectName() == "home_button":
            self.label_3.setText("Trang Chủ")
        elif sender.objectName() == "manage_user_button":
            self.label_3.setText("Quản lý người dùng")

    def change_button_style_on_click(self):
        sender = self.sender()  # Get the button that triggered the event

        for button in [self.home_button, self.manage_user_button]:
            if button == sender:
                button.setStyleSheet("""
                    background-color:#6CB4EE;
                    border-top-left-radius: 15px;
                """)

            # Set the new button as active and change its style
            else:
                button.setStyleSheet("""
                     background-color:#FAF9F6;
            """)

    def select_all_items(self):
        """Select all items in the QTreeView."""
        self.treeView.selectAll()
