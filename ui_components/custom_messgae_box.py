from PyQt6.QtWidgets import QMessageBox, QPushButton
from PyQt6.QtGui import QIcon


class CustomMessageBox(QMessageBox):
    def __init__(self, title, message, icon_type, button_text="OK", parent=None):
        super().__init__(parent)

        # Set basic properties
        self.setWindowTitle(title)
        self.setText(message)
        self.setIcon(icon_type)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        ok_button = self.button(QMessageBox.StandardButton.Ok)
        ok_button.setText(button_text)

        # Apply custom styles
        self.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: black;
                font-size: 14px;
                border-radius: 10px;
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
        """)
