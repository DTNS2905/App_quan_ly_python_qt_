class UserSession:
    def __init__(self, username, permissions: list[str]):
        print(f"DEBUG: User '{username}' - Permissions '{permissions}'")
        self._username = username
        self._permissions = permissions

    def match_permissions(self, checked_permission):
        print(f"DEBUG: check permission {checked_permission}")
        return checked_permission in self._permissions

    def update_permissions(self, new_permissions):
        self._permissions = new_permissions

    def clear(self):
        del self._username
        del self._permissions


SESSION = None
