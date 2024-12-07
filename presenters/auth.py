from common.auth import verify_password
from common.presenter import Presenter
from messages.messages import LOGIN_SUCCESS, LOGIN_ERROR, USERNAME_TAKEN, REGISTER_SUCCESS, REGISTER_ERROR
from models.auth import AuthModel
from models.permission import PermissionModel


class AuthPresenter(Presenter):
    def __init__(self, view):
        super().__init__(view, AuthModel())
        self._verify_password = verify_password
        self.permission_model = PermissionModel()

    def handle_login(self):
        username = self.view.username_input.text()
        password = self.view.password_input.text()

        hashed_password = self.model.verify_user(username)
        if hashed_password and self._verify_password(password, hashed_password):
            self.view.display_success(LOGIN_SUCCESS)
            self.view.accept()  # Close dialog and signal success
            permissions = self.permission_model.get_permission_by_username(username).permissions
            item_permissions = self.permission_model.get_item_permission_by_username(username).permissions
            return username, permissions, item_permissions
        else:
            self.view.display_error(LOGIN_ERROR)
            return

    def handle_register(self, username: str, password: str, confirm_password: str):
        """
        Handles user registration.

        Args:
            username (str): The username to register.
            password (str): The password for the user.
            confirm_password (str): The confirmation of the password.

        Returns:
            None
        """
        # Validate input fields
        if not username or not password or not confirm_password:
            self.view.display_error("Tên đăng nhập, mật khẩu và xác nhận mật khẩu không được để trống.")
            return

        # Ensure passwords match
        if password != confirm_password:
            self.view.display_error("Mật khẩu và xác nhận mật khẩu không khớp.")
            return

        # Check if the username is already taken
        if self.model.verify_user(username):
            self.view.display_error(USERNAME_TAKEN)
            return

        try:
            # Add the user to the model
            self.model.add_user(username, password)
            self.view.display_success(REGISTER_SUCCESS)
            permissions = self.permission_model.get_permission_by_username(username).permissions
            self.view.accept()
            return username,permissions
        except Exception as e:
            self.view.display_error(f"{REGISTER_ERROR}: {str(e)}")

    def add_default_user(self, username, password):
        self.model.add_user(username, password)
