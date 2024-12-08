import datetime

SW_NAME = "Phần Mềm Quản Lý Bài"
BUILD_NUMBER = "20241208095109"
VERSION = "1.0.0"
AUTHORS = [
    "Đoàn Văn Thanh Liem - liem18112000@gmail.com",
    "Đoàn Nguyễn Thanh Sang - sangdoan29052005@gmail.com",
]


def show_version_info(parent):
    from PyQt6.QtWidgets import QMessageBox

    authors = "\n- ".join(AUTHORS)
    QMessageBox.information(
        parent,
        "Thông Tin",
        f"{SW_NAME}"
        f"\nPhiên Bản: {VERSION}"
        f"\nBản dựng: {BUILD_NUMBER}"
        f"\n\nĐược phát triển: \n- {authors}"
        f"\n\nCopyright © 2024 LiemSoftware"
        f"\nLicensed under the MIT License",
    )


def create_about_action(parent, help_menu):
    from PyQt6.QtGui import QAction

    version_action = QAction("About", parent)
    version_action.triggered.connect(lambda: show_version_info(parent))
    help_menu.addAction(version_action)
