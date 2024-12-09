from PyQt6.QtWidgets import (
    QInputDialog,
    QDialogButtonBox,
    QPushButton,
    QVBoxLayout,
    QDialog,
    QLabel,
    QLineEdit,
    QHBoxLayout,
)


class CustomInputDialog(QDialog):
    def __init__(
        self,
        parent,
        window_title,
        label_text,
        ok_text="Xác nhận",
        cancel_text="Hủy",
        input_default_text="",
    ):
        super().__init__(parent)
        self.setWindowTitle(window_title)  # Title of the dialog

        # Create the layout
        layout = QVBoxLayout()

        # Label and input field
        self.label = QLabel(label_text)  # Prompt label
        self.input_field = QLineEdit()  # Input field for folder name
        self.input_field.setText(input_default_text)
        layout.addWidget(self.label)
        layout.addWidget(self.input_field)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton(ok_text)  # OK button with custom text
        self.cancel_button = QPushButton(cancel_text)  # Cancel button with custom text
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Set the main layout
        self.setLayout(layout)

        # Connect buttons to dialog slots
        self.ok_button.clicked.connect(self.accept)  # Close dialog with Accepted result
        self.cancel_button.clicked.connect(
            self.reject
        )  # Close dialog with Rejected result

    def get_text(self):
        """Return the entered text."""
        return self.input_field.text().strip()
