from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton


class HoverButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hover_style = """v
            QPushButton:hover {
                background-color: #74b9ff; /* Light blue */
                border: 1px solid #0984e3; /* Bright blue border */
            }
        """
        existing_stylesheet = self.styleSheet()
        self.setStyleSheet(existing_stylesheet + self.hover_style)
        self.setCursor(Qt.CursorShape.PointingHandCursor)  # Pointer cursor on hover