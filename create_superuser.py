import sys
from getpass import getpass

from PyQt6.QtWidgets import QApplication
from models.auth import AuthModel  # Assuming your AuthModel is saved in auth_model.py


def main():
    app = QApplication(sys.argv)  # Needed for QSqlQuery to work
    auth_model = AuthModel()

    # Create superuser
    username = input("Enter superuser username:\n ")
    print("Enter superuser password: ")
    password = getpass()

    auth_model.create_superuser(username, password)


if __name__ == "__main__":
    main()
