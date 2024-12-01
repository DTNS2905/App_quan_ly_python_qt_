from common.auth import verify_password
from common.presenter import Presenter
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
            self.view.display_success("Đang nhập thành công")
            self.view.accept()  # Close dialog and signal success
            permissions = self.permission_model.get_permission_by_username(username).permissions
            return username, permissions
        else:
            self.view.display_error("Tên người dùng hoặc mật khẩu không hợp lệ")

    def add_default_user(self, username, password):
        self.model.add_user(username, password)
