class UserSession:
    def __init__(self, username, permissions: list[str], is_admin: bool = False):
        print(f"DEBUG: User '{username}' - Permissions '{permissions}'")
        self._username = username
        self._permissions = permissions
        self._is_admin = is_admin

    def match_permissions(self, checked_permission):
        print(f"DEBUG: check permission {checked_permission}")
        print(f"DEBUG: is admin {self._is_admin}")
        return self._is_admin or checked_permission in self._permissions

    def update_permissions(self, new_permissions):
        self._permissions = new_permissions

    def clear(self):
        del self._username
        del self._permissions


SESSION = None
