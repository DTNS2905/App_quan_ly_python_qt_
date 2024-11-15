import sys
from PyQt5 import QtWidgets
from views.auth import LoginDialog
from views.main_window import MainWindow  # Import MainWindow if needed

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    login_dialog = LoginDialog()
    if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
        main_window = MainWindow()
        main_window.show()

    sys.exit(app.exec_())
