import logging


class UserSession:
    def __init__(self, username, permissions: list[str],
                 item_permissions: dict[str, list[str]] = {}):
        logging.debug(f"DEBUG: User '{username}'\n- Permissions '{permissions}'\n- Items '{item_permissions}'")
        self._username = username
        self._permissions = permissions
        self._item_permissions = item_permissions

    def get_username(self):
        return self._username

    def get_permissions(self):
        return self._permissions

    def get_item_permissions(self, item):
        if item not in self._item_permissions.keys():
            return []
        return self._item_permissions[item]

    def match_permissions(self, checked_permission):
        logging.debug(f"DEBUG: check permission {checked_permission}")
        return checked_permission in self._permissions

    def match_item_permissions(self, item: str, checked_permission: str):
        logging.debug(f"DEBUG: check {item} permission {checked_permission}")
        return (item in self._item_permissions.keys()
                and checked_permission in self._item_permissions[item])

    def update_permissions(self, new_permissions):
        self._permissions = new_permissions

    def update_item_permissions(self, item, new_permissions):
        self._item_permissions[item] = new_permissions

    def clear(self):
        del self._username
        del self._permissions


SESSION: UserSession = None
