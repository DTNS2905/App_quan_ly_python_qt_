from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt, QObject, QEvent
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QMessageBox, QHeaderView

from presenters.item import ItemPresenter
from presenters.permission import PermissionPresenter
from ui_components.custom_messgae_box import CustomMessageBox
from views.profile_dialog import ProfileDialog


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phần mềm hỗ trợ quản lý bài giảng")
        uic.loadUi('ui/admin_dashboard.ui', self)
        # self.tree_presenter = FileTreePresenter(self)
        self.item_presenter = ItemPresenter(self)
        self.permission_presenter = PermissionPresenter(self)
        self.permission_presenter.populate_table()

        # Connect buttons to slots
        self.home_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.stackedWidgetPage1))
        self.manage_user_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.stackedWidgetPage2))

        self.home_button.clicked.connect(self.update_label_text)
        self.manage_user_button.clicked.connect(self.update_label_text)

        self.home_button.clicked.connect(self.change_button_style_on_click)
        self.manage_user_button.clicked.connect(self.change_button_style_on_click)

        self.add_file_button.clicked.connect(self.item_presenter.handle_add_files)
        self.remove_file_button.clicked.connect(self.item_presenter.handle_remove_files)

        self.add_folder_button.clicked.connect(self.item_presenter.handle_add_folder)
        self.remove_folder_button.clicked.connect(self.item_presenter.handle_remove_folder)

        self.label_2.installEventFilter(self)

        # Set up treeView at FILES_ROOT_PATH
        self.item_presenter.setup_view()
        self.treeView.doubleClicked.connect(self.item_presenter.open_file)

        # Add Ctrl+A shortcut for Select All in treeView
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self.treeView)
        select_all_shortcut.activated.connect(self.select_all_items)

    def set_model(self, model):
        self.treeView.setModel(model)

    def display_success(self, message):
        """Display a custom success message."""
        success_box = CustomMessageBox("Thành công", message, QMessageBox.Icon.Information, "Đóng", self)
        success_box.exec()

    def display_error(self, message):
        """Display a custom error message."""
        error_box = CustomMessageBox("Lỗi", message, QMessageBox.Icon.Warning, "Đóng", self)
        error_box.exec()

    def update_tree_view(self, root_index):
        """Update the tree view to a specific root index."""
        # self.treeView.setRootIndex(root_index)

    def refresh_tree_view(self):
        """Refresh the tree view to reflect any changes in the file system."""
        self.set_model(self.item_presenter.refresh_model())

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

    # def open_main_dialog(self):
    #     self.main_dialog = MyMainDialog()
    #     self.main_dialog.show()  # Opens the main window as if it's a dialog

    def open_dialog(self):
        dialog = ProfileDialog(self)  # Pass the main window as the parent
        dialog.show()  # Open as a modal dialog

    def eventFilter(self, source, event):
        if source == self.label_2 and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.open_dialog()  # Call the dialog method
                return True  # Event is handled
        return super().eventFilter(source, event)
