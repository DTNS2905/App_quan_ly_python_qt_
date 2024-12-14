import traceback
import markdown
from PyQt6.QtWidgets import QTextBrowser, QDialog, QVBoxLayout


class InstructDialog(QDialog):
    def __init__(self, parent=None, markdown_file: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Màn Hình Hướng Dẫn")
        self.text_browser = QTextBrowser()

        try:
            with open(markdown_file, mode="r", encoding="utf-8") as f:
                self.content = f.read()

            self.show_dialog()
        except:
            print(traceback.print_exc())

    def show_dialog(self):
        html_content = markdown.markdown(self.content)

        # Set the HTML content to the text browser
        self.text_browser.setHtml(html_content)

        # Create a layout for the dialog
        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)
        self.setLayout(layout)

        # Show the dialog
        self.resize(1080, 720)
        self.show()
