from PyQt6.QtWidgets import QInputDialog, QDialogButtonBox, QPushButton, QVBoxLayout, QDialog, QLabel, QLineEdit, \
    QHBoxLayout


class CustomInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thư mục mới")  # Title of the dialog

        # Create the layout
        layout = QVBoxLayout()

        # Label and input field
        self.label = QLabel("Điền tên thư mục:")  # Prompt label
        self.input_field = QLineEdit()  # Input field for folder name
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Thêm")  # OK button with custom text
        self.cancel_button = QPushButton("Hủy")  # Cancel button with custom text
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Set the main layout
        self.setLayout(layout)

        # Connect buttons to dialog slots
        self.ok_button.clicked.connect(self.accept)  # Close dialog with Accepted result
        self.cancel_button.clicked.connect(self.reject)  # Close dialog with Rejected result

    def get_text(self):
        """Return the entered text."""
        return self.input_field.text().strip()
