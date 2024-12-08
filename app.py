import logging
import sys
import resources
from PyQt6 import QtWidgets

from configs import setup_logging
from views.auth import LoginDialog
from views.main_window import MainWindow
setup_logging()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    try:
        # Show login dialog
        login_dialog = LoginDialog()
        if login_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            # Proceed to main window if login is successful
            main_window = MainWindow()

            main_window.show()
        else:
            logging.info("Login cancelled.")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        sys.exit(1)

    sys.exit(app.exec())
