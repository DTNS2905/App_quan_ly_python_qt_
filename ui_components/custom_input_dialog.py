from PyQt6.QtWidgets import QInputDialog, QPushButton, QDialogButtonBox


class CustomInputDialog(QInputDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Access and customize the button box
        button_box = self.findChild(QDialogButtonBox)
        if button_box:
            # Remove default buttons
            for button in button_box.buttons():
                button_box.removeButton(button)

            # Add custom buttons
            self.ok_button = QPushButton("Thêm")  # "Add" in Vietnamese
            self.cancel_button = QPushButton("Hủy")  # "Cancel" in Vietnamese
            button_box.addButton(self.ok_button, QDialogButtonBox.ButtonRole.AcceptRole)
            button_box.addButton(self.cancel_button, QDialogButtonBox.ButtonRole.RejectRole)

        # Connect signals
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)