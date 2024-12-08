SW_NAME = "Phần Mềm Quản Lý Bài"
BUILD_NUMBER = "20241208095109"
VERSION = "1.0.0"


def show_version_info(parent):
    from PyQt6.QtWidgets import QMessageBox

    QMessageBox.information(
        parent,
        "Thông Tin",
        f"{SW_NAME}" f"\nPhiên Bản: {VERSION}" f"\nBản dựng: {BUILD_NUMBER}",
    )


def create_about_action(parent, help_menu):
    from PyQt6.QtGui import QAction

    version_action = QAction("About", parent)
    version_action.triggered.connect(lambda: show_version_info(parent))
    help_menu.addAction(version_action)
