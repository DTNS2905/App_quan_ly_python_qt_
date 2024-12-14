import logging
import traceback

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt, QObject, QEvent, pyqtSignal, QStringListModel
from PyQt6.QtGui import QShortcut, QKeySequence
from PyQt6.QtWidgets import QMessageBox, QHeaderView, QDialog, QCompleter, QAbstractItemView

from common import session
from configs import DASHBOARD_UI_PATH
from messages.messages import PERMISSION_DENIED
from messages.permissions import (
    LOG_VIEW,
    PERMISSION_VIEW,
    PERMISSION_GRANT,
    PERMISSION_UNGRANT,
    FILE_DOWNLOAD,
    FILE_CREATE,
    FOLDER_CREATE,
    FILE_RENAME,
    FOLDER_RENAME, FILE_DELETE, FOLDER_DELETE,
)
from presenters.item import ItemPresenter
from presenters.permission import PermissionPresenter
from ui_components.custom_messgae_box import CustomMessageBox
from version import create_about_action
from views.add_deadlline import AssignmentDialog
from views.auth import LoginDialog
from views.item_permission import ItemPermissionDialog
from views.log_dialog import LogDialog
from views.permission_dialog import PermissionDialog
from views.permission_item_dialog import PermissionItemDialog
from views.profile_dialog import ProfileDialog


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phần mềm hỗ trợ quản lý bài giảng")

        uic.loadUi(DASHBOARD_UI_PATH, self)

        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu("Help")
        create_about_action(self, help_menu)

        self.item_presenter = ItemPresenter(self)
        self.permission_presenter = PermissionPresenter(self)
        self.permission_presenter.populate_table()

        self.showMaximized()

        self.username.setText(session.SESSION.get_username())

        # Connect buttons to slots
        self.home_button.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.stackedWidgetPage1)
        )
        self.manage_user_button.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.stackedWidgetPage2)
        )

        self.home_button.clicked.connect(self.update_label_text)
        self.manage_user_button.clicked.connect(self.update_label_text)

        self.home_button.clicked.connect(self.change_button_style_on_click)
        self.manage_user_button.clicked.connect(self.change_button_style_on_click)

        # add file button
        self.add_file_button.clicked.connect(
            self.item_presenter.handle_add_files
        )
        self.add_file_button.setVisible(
            session.SESSION.match_permissions(FILE_CREATE)
        )

        # rename file button
        self.rename_file_button.clicked.connect(
            self.item_presenter.handle_rename_file
        )
        self.rename_file_button.setVisible(
            session.SESSION.match_permissions(FILE_RENAME)
        )

        # Remove file button
        self.remove_file_button.clicked.connect(
            self.item_presenter.handle_remove_files
        )
        self.remove_file_button.setVisible(
            session.SESSION.match_permissions(FILE_DELETE)
        )

        # Remove folder button
        self.add_folder_button.clicked.connect(
            self.item_presenter.handle_add_folder
        )
        self.add_folder_button.setVisible(session.SESSION.match_permissions(
            FOLDER_CREATE)
        )

        # rename folder button
        self.rename_folder_button.clicked.connect(
            self.item_presenter.handle_rename_folder
        )
        self.rename_folder_button.setVisible(
            session.SESSION.match_permissions(FOLDER_RENAME)
        )

        # Remove folder button
        self.remove_folder_button.clicked.connect(
            self.item_presenter.handle_remove_folder
        )
        self.remove_folder_button.setVisible(
            session.SESSION.match_permissions(FOLDER_DELETE)
        )

        # Initialize QCompleter
        self.completer = QCompleter(self)
        self.completer.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )  # Corrected: Use enum
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Match substrings
        self.completer.setCompletionMode(
            QCompleter.CompletionMode.PopupCompletion
        )  # Use popup for suggestions

        # Set the model for the completer
        self.string_list_model = QStringListModel()  # Start with an empty model
        self.completer.setModel(self.string_list_model)

        # Attach the completer to the lineEdit
        self.search_input.setCompleter(self.completer)

        self.search_input.textChanged.connect(self.on_search_text_changed)

        self.search_button.clicked.connect(self.search_files_folders)

        # self.assignment_button.clicked.connect(lambda: self.open_adđ_deadline_dialog(AssignmentDialog))

        self.label_2.installEventFilter(self)

        def do_permission(action):
            permission = (
                PERMISSION_GRANT
                if action == "assign_permission"
                else PERMISSION_UNGRANT
            )
            if not session.SESSION.match_permissions(permission):
                self.display_error(f"{permission}: {PERMISSION_DENIED}")
                return

            items = [
                self.treeView.model().data(value)
                for index, value in enumerate(self.treeView.selectedIndexes())
                if index % 4 == 0
            ]
            if len(items) == 0:
                self.display_error("Xin chọn 1 tệp")
            else:
                dialog = PermissionItemDialog(self, items, action)
                self.open_permission_dialog(dialog)

        self.add_perrmission_button.clicked.connect(
            lambda: do_permission("assign_permission")
        )

        self.add_perrmission_button.setVisible(
            session.SESSION.match_permissions(PERMISSION_GRANT)
        )

        self.remove_permission_button_2.clicked.connect(
            lambda: do_permission("unassign_permission")
        )

        self.remove_permission_button_2.setVisible(
            session.SESSION.match_permissions(PERMISSION_UNGRANT)
        )

        self.add_permission_button.clicked.connect(
            lambda: self.open_permission_dialog(
                PermissionDialog(self, "assign_permission")
            )
        )

        self.add_permission_button.setVisible(
            session.SESSION.match_permissions(PERMISSION_GRANT)
        )

        self.remove_permission_button.clicked.connect(
            lambda: self.open_permission_dialog(
                PermissionDialog(self, "unassign_permission")
            )
        )

        self.remove_permission_button.setVisible(
            session.SESSION.match_permissions(PERMISSION_UNGRANT)
        )

        self.download_button.clicked.connect(
            self.item_presenter.handle_download_items
        )

        self.download_button.setVisible(
            session.SESSION.match_permissions(FILE_DOWNLOAD)
        )

        self.logout_button.clicked.connect(lambda: self.log_out(LoginDialog(self)))

        def view_log():
            if not session.SESSION.match_permissions(LOG_VIEW):
                self.display_error(PERMISSION_DENIED)
            else:
                self.open_dialog(LogDialog(self))

        self.log_button.clicked.connect(lambda: view_log())
        self.log_button.setVisible(
            session.SESSION.match_permissions(LOG_VIEW)
        )

        def view_item_permission():
            if not session.SESSION.match_permissions(PERMISSION_VIEW):
                self.display_error(PERMISSION_DENIED)
            else:
                self.open_dialog(ItemPermissionDialog(self))

        self.item_permission_button.clicked.connect(lambda: view_item_permission())

        self.item_permission_button.setVisible(
            session.SESSION.match_permissions(PERMISSION_VIEW)
        )

        # Set up treeView at FILES_ROOT_PATH
        self.item_presenter.setup_view()

        self.treeView.doubleClicked.connect(self.handle_open_file)

        # Add Ctrl+A shortcut for Select All in treeView
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self.treeView)
        select_all_shortcut.activated.connect(self.select_all_items)

    def set_model(self, model):
        self.treeView.setModel(model)

    def display_success(self, message):
        """Display a custom success message."""
        success_box = CustomMessageBox(
            "Thành công", message, QMessageBox.Icon.Information, "Đóng", self
        )
        success_box.exec()

    def display_error(self, message):
        """Display a custom error message."""
        error_box = CustomMessageBox(
            "Lỗi", message, QMessageBox.Icon.Warning, "Đóng", self
        )
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
                button.setStyleSheet(
                    """
                    background-color:#6CB4EE;
                    border-top-left-radius: 15px;
                """
                )

            # Set the new button as active and change its style
            else:
                button.setStyleSheet(
                    """
                     background-color:#FAF9F6;
            """
                )

    def select_all_items(self):
        """Select all items in the QTreeView."""
        self.treeView.selectAll()

    def open_profile_dialog(self):
        dialog = ProfileDialog(self)  # Pass the main window as the parent
        dialog.show()  # Open as a modal dialog

    def eventFilter(self, source, event):
        if source == self.label_2 and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.open_profile_dialog()  # Call the dialog method
                return True  # Event is handled
        return super().eventFilter(source, event)

    def open_permission_dialog(self, dialog_instance):
        if isinstance(dialog_instance, QDialog):
            dialog_instance.finished.connect(self.refresh_permission_view)
            dialog_instance.exec()  # For modal dialogs
        else:
            logging.warning("Provided instance is not a QDialog.")

    def open_dialog(self, dialog_instance):
        if isinstance(dialog_instance, QDialog):
            dialog_instance.exec()  # For modal dialogs
        else:
            logging.warning("Provided instance is not a QDialog.")

    def log_out(self, dialog_instance):
        # Create a confirmation dialog
        message_box = QMessageBox(self)
        message_box.setWindowTitle("Xác Nhận")  # Translated dialog title
        message_box.setText("Bạn có chắc chắn muốn đăng xuất không?")
        message_box.setIcon(QMessageBox.Icon.Question)

        # Custom buttons with Vietnamese text
        yes_button = message_box.addButton("Đồng Ý", QMessageBox.ButtonRole.YesRole)
        no_button = message_box.addButton("Hủy", QMessageBox.ButtonRole.NoRole)
        message_box.setStyleSheet(
            """
            QMessageBox {
                background-color: white;
                color: black;
                font-size: 14px;
                border-radius: 10px;
            }
            QLabel {
                color: black;
                font-size: 14px;
            }
            QPushButton {
                background-color: #E0E0E0;
                color: black;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #C0C0C0;
            }
        """
        )

        # Show the dialog and wait for user input
        message_box.exec()

        # Check which button was clicked
        if message_box.clickedButton() == yes_button:
            try:
                self.close()
                session.SESSION = None
                if dialog_instance.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                    # Proceed to main window if login is successful
                    main_window = MainWindow()
                    main_window.show()
                else:
                    logging.info("Login cancelled.")
            except:
                logging.error(traceback.print_exc())
        elif message_box.clickedButton() == no_button:
            logging.info("user does not log out")
            return

    def refresh_permission_view(self):
        self.permission_presenter.populate_table()

    def expand_and_highlight(self, matches):
        """
        Expand and scroll to matching nodes.

        Args:
            matches (list[QModelIndex]): A list of QModelIndex objects for matching nodes.
        """
        for match in matches:
            self.treeView.expand(match)  # Expand matching node
            self.treeView.scrollTo(match, QAbstractItemView.ScrollHint.PositionAtCenter)  # Scroll to it

    def search_files_folders(self):
        """
        Notify the presenter about the search text and expand/scroll to matches.
        This will clear highlights if the search input is empty.
        """
        search_text = self.search_input.text()

        self.item_presenter.search_tree(search_text)  # Perform search if text is not empty

    def on_search_text_changed(self):
        """
        Handle text changes in the search input.
        Clears highlights and updates suggestions based on the current input text.
        """
        search_text = self.search_input.text()

        if not search_text.strip():  # If input is empty, clear highlights and suggestions
            self.item_presenter.clear_highlights()  # Reset all highlights
            return

        # Update suggestions as the user types
        self.item_presenter.update_suggestions(search_text)

    def handle_open_file(self, index):
        # Retrieve the file name from the QStandardItemModel
        model = self.item_presenter.get_model_for_view()
        original_name = model.itemFromIndex(index).text()

        # Call the Presenter to open the file
        self.item_presenter.open_file(original_name)

    def open_adđ_deadline_dialog(self, dialog_instance):
        selected_indexes = self.treeView.selectionModel().selectedIndexes()

        # Get the first selected item (assuming single selection mode)
        selected_index = selected_indexes[0]

        item = self.treeview.model().itemFromIndex(selected_index)

        # Extract the file or folder name
        file_or_folder_name = item.text()
        print(f"item select: {file_or_folder_name}")

        # Pass the name to the dialog instance or perform any logic
        dialog_instance.set_selected_item(file_or_folder_name)

        # Open the dialog
        self.open_dialog(dialog_instance)
