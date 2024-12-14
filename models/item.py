import logging
import os.path
import shutil
import sqlite3
import sys
import traceback
import uuid
from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont, QIcon, QBrush
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QFileIconProvider

from common import session
from common.file import get_file_type, is_valid_filename, is_valid_folder_name
from common.model import NativeSqlite3Model
from common.time import convert_utc_time_to_timezone
from configs import DATABASE_NAME, FILES_ROOT_PATH, FILE_TREE_VIEW_COLUMNS, TIMEZONE
from messages.permissions import FILE_VIEW, FOLDER_VIEW
from sql_statements.assignment import GET_TIME_STATUS_BASED_ON_ITEM_ID_AND_USERNAME
from sql_statements.item import (
    CREATE_ITEM_TABLE_SQL,
    CREATE_PERMISSION_USER_ITEM_TABLE_SQL,
    INIT_DATA, FETCH_NAME_FILE_OR_FOLDER_ON_TEXTCHANGED,
)


@dataclass
class ItemDTO:
    id: int
    code: str
    parent_id: int
    user_id: int
    type: str
    original_name: str
    created_at: str
    updated_at: str


def build_tree(items: list[ItemDTO]) -> list[ItemDTO]:
    """
    Build a tree structure from a flat list of ItemDTO objects.

    Args:
        items (list[ItemDTO]): List of ItemDTO objects with parent-child relationships.

    Returns:
        list[ItemDTO]: List of children under the root (parent_id == -1).
    """
    # Create a dictionary for quick lookup of items by their ID
    item_dict = {item.id: item for item in items}

    # Initialize children for all items
    for item in items:
        item.children = []

    # Build the tree structure
    root_children = []
    for item in items:
        if item.parent_id == -1:
            # Skip the "root" node, but track its children
            continue
        else:
            # Assign the item as a child of its parent
            parent = item_dict.get(item.parent_id)
            if parent:
                parent.children.append(item)

            # If the parent is the "root," add it to the root_children list
            if parent and parent.parent_id == -1:
                root_children.append(item)

    return root_children


class CustomItem(QStandardItem):
    def __init__(
            self, content, font_size=12, bold=False, color=QColor(0, 0, 0), *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        font = QFont("Open Sans", font_size)
        font.setBold(bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(font)
        self.setText(content)

    def set_custom_icon(self, icon):
        self.setIcon(icon)


class ItemModel(NativeSqlite3Model):
    _junction_table_sql = CREATE_PERMISSION_USER_ITEM_TABLE_SQL
    _init_data_sql = INIT_DATA
    _root_path = FILES_ROOT_PATH
    _fetch_sql = """
    SELECT i.id, i.code, i.parent_id, i.user_id, i.type, i.original_name, i.created_at, i.updated_at FROM items AS i
"""

    def __init__(
            self, database_name=DATABASE_NAME, table_create_sql=CREATE_ITEM_TABLE_SQL
    ):
        super().__init__(database_name, table_create_sql)
        self._init_junction_table()
        self._init_data()
        self.model = QStandardItemModel(0, len(FILE_TREE_VIEW_COLUMNS))
        self.model.setHorizontalHeaderLabels(FILE_TREE_VIEW_COLUMNS)

    def _init_junction_table(self):
        cur = self.connection.cursor()
        try:
            cur.execute(self._junction_table_sql)
            self.connection.commit()
        except sqlite3.Error as error:
            raise Exception(f"Failed to create junction table: {error}")
        finally:
            cur.close()

    def _init_data(self):
        cur = self.connection.cursor()
        try:
            cur.execute(self._init_data_sql)
            self.connection.commit()
        except sqlite3.Error as error:
            raise Exception(f"Failed to init data: {error}")
        finally:
            cur.close()

    def get_model(self):
        """Returns the file system model."""
        return self.model

    def get_root_node(self):
        return self.model.invisibleRootItem()

    def get_path_for_files_storage(self):
        return self._root_path

    def populate_data(self):
        """
        Populate the tree view with all files and folders directly under the root.
        Ensures rows with no data or invalid children are skipped.
        """
        try:
            items = self.fetch_data()
            print(f"Fetched items: {items}")
            logging.debug(f"Fetched items: {items}")
            root_children = build_tree(items)
            print(f"Root children: {root_children}")
            logging.debug(f"Root children: {root_children}")
            font_size = 14

            icon_provider = QFileIconProvider()

            def create_item(content, font_size, icon_type, bold=False, color=QColor(0, 0, 0), user_role=None):
                """
                Helper to create a CustomItem with specific attributes.
                """
                item = CustomItem(content, font_size=font_size, bold=bold, color=color)
                item.set_custom_icon(icon_provider.icon(icon_type))
                if user_role:
                    item.setData(user_role, Qt.ItemDataRole.UserRole)
                return item

            def create_metadata(child, font_size):
                """
                Fetch and create metadata columns for a file.
                """
                file_type = get_file_type(child.original_name)
                created_at = convert_utc_time_to_timezone(
                    child.created_at, TIMEZONE
                ).strftime("%Y-%m-%d %H:%M:%S")

                cur = self.connection.cursor()
                cur.execute(
                    "SELECT fullname FROM profiles WHERE user_id = ?", (child.user_id,)
                )
                result = cur.fetchone()

                fullname = result[0] if result else "Unknown"
                cur.execute(
                    ''' SELECT a.begin_time, a.end_time
                        FROM assignments AS a
                        JOIN users AS u
                        ON a.assigned_by = u.user_id OR a.assigned_to = u.user_id
                        WHERE a.assignment_id = ? AND u.user_name = ?''',
                    (child.id, fullname))
                assignment_result = cur.fetchone()
                response = assignment_result[0] if assignment_result else None

                return (
                    CustomItem(file_type, font_size=font_size - 1, color=QColor(50, 50, 50)),
                    CustomItem(created_at, font_size=font_size - 1, color=QColor(50, 50, 50)),
                    CustomItem(fullname, font_size=font_size - 1, color=QColor(50, 50, 50)),
                    CustomItem(response['user_assign'], font_size=font_size - 1, color=QColor(50, 50, 50)),
                    CustomItem(response['assigned_user'], font_size=font_size - 1, color=QColor(50, 50, 50)),
                    CustomItem(response['begin_time'], font_size=font_size - 1, color=QColor(50, 50, 50)),
                    CustomItem(response['end_time'], font_size=font_size - 1, color=QColor(50, 50, 50)),
                )

            def process_child(parent_node, child, font_size):
                """
                Process and append a child node (file or folder) to the parent node.
                """
                try:
                    # Check permissions
                    permission = FOLDER_VIEW if child.type == "folder" else FILE_VIEW
                    if not (
                            session.SESSION.match_permissions(permission)
                            or session.SESSION.match_item_permissions(child.original_name, permission)
                    ):
                        return

                    # Determine icon type and user role
                    icon_type = (
                        QFileIconProvider.IconType.Folder
                        if child.type == "folder"
                        else QFileIconProvider.IconType.File
                    )
                    user_role = "directory" if child.type == "folder" else "file"

                    # Create the item for the child
                    item = create_item(
                        content=child.original_name,
                        font_size=font_size,
                        icon_type=icon_type,
                        bold=child.type == "folder",
                        user_role=user_role,
                    )
                    # information about assignment

                    if child.type == "file":
                        # Add metadata columns for files
                        item_type, item_created_at, item_created_by, user_assign, assigned_user, begin_time, end_time\
                            = create_metadata(child, font_size)
                        print(f'process_child: \n{create_metadata(child, font_size)}')
                        parent_node.appendRow(
                            [
                                item, item_type, item_created_at, item_created_by,
                                user_assign, assigned_user, begin_time, end_time
                            ]
                        )
                    elif child.type == "folder":
                        # Add the folder node
                        parent_node.appendRow([item])
                        return item  # Return folder item to process its children

                except Exception as e:
                    logging.error(f"Error processing child: {child.original_name} - {e}")
                    logging.error(traceback.format_exc())

            def traverse(children, parent_node, font_size):
                """
                Iteratively traverse the children and populate the tree view under the given parent node.
                """
                stack = [(child, parent_node) for child in children]

                while stack:
                    child, current_parent = stack.pop()
                    folder_item = process_child(current_parent, child, font_size)
                    if folder_item and child.type == "folder":
                        # Push children of the folder to the stack
                        stack.extend((grandchild, folder_item) for grandchild in child.children)

            # Process all root children
            if not root_children:
                logging.info("No data found to populate the tree.")
                return

            # Get the root node
            root_node = self.get_root_node()
            if not root_node:
                logging.error("Root node is missing. Cannot populate data.")
                return

            # Traverse the root children
            traverse(root_children, root_node, font_size)

            # Notify the view to expand the tree view
            self.notify_tree_expansion()

        except Exception as e:
            logging.error(f"Error populating data: {e}")
            logging.error(traceback.format_exc())

    def refresh_model(self):
        self.model = QStandardItemModel(0, len(FILE_TREE_VIEW_COLUMNS))
        self.model.setHorizontalHeaderLabels(FILE_TREE_VIEW_COLUMNS)
        self.populate_data()
        return self.model

    def get_root_path(self):
        return self._root_path

    def create_file(
            self, username: str, file_path: str, parent_original_name: str = "root"
    ):
        """
        Creates a new file in the system and updates the database and tree structure.

        Args:
            username (str): The username of the file creator.
            file_path (str): The path to the file to be added.
            parent_original_name (str, optional): The name of the parent folder. Defaults to None.

        Returns:
            int: The ID of the newly created file in the database.

        Raises:
            Exception: If the file creation fails at any step.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")

        cur = None
        try:
            # Get the user ID
            cur = self.connection.cursor()
            cur.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_row = cur.fetchone()
            if not user_row:
                raise ValueError(f"User '{username}' not found.")
            user_id = user_row[0]

            # Get the parent ID
            if parent_original_name:
                cur.execute(
                    "SELECT id, type FROM items WHERE original_name = ?", (parent_original_name,)
                )
                parent_row = cur.fetchone()
                if not parent_row:
                    raise ValueError(f"Parent '{parent_original_name}' not found.")
                parent_id, parent_type = parent_row
                if parent_type == "file":
                    raise ValueError(f"Cannot add a file under another file: {parent_original_name}.")
            else:
                parent_id = 0  # Root directory

            # Prepare file details
            original_name = os.path.basename(file_path)
            code = str(uuid.uuid4())

            # Insert file record into the database
            cur.execute(
                "INSERT INTO items (code, type, original_name, parent_id, user_id) VALUES (?, ?, ?, ?, ?)",
                (code, "file", original_name, parent_id, user_id),
            )
            if cur.rowcount == 0:
                raise Exception(f"Failed to insert file '{original_name}' into the database.")

            # Commit changes and copy the file to the system's storage location
            file_id = cur.lastrowid
            self.connection.commit()
            shutil.copy(file_path, os.path.join(self._root_path, code))

            # Log success
            logging.info(f"File '{original_name}' created successfully with ID {file_id}.")

            return file_id

        except Exception as e:
            if cur:
                self.connection.rollback()
            logging.error(f"Error creating file '{file_path}': {e}")
            raise e

        finally:
            if cur:
                cur.close()

    def get_item_details(self, original_name):
        """
        Fetches the item details by the original name.
        :param original_name: The original name of the file.
        :return: Tuple of (id, code, type) or None if not found.
        """
        cur = self.connection.cursor()
        cur.execute(
            "SELECT id, code, type FROM items WHERE original_name = ?", (original_name,)
        )
        return cur.fetchone()

    def get_file_bytes(self, original_name):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT id, code, type FROM items WHERE original_name = ?", (original_name,)
        )
        item_id, code, file_type = cur.fetchone()
        if file_type != "file":
            return None
        file_path = os.path.join(self._root_path, code)
        with open(file_path, "rb") as f:
            return f.read()

    def create_folder(
            self, username: str, original_name: str, parent_original_name: str = None):
        cur = self.connection.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cur.fetchone()[0]
        cur.execute(
            "SELECT id FROM items WHERE original_name = ?", (parent_original_name,)
        )
        result = cur.fetchone()
        if result:
            parent_id = result[0]
        else:
            parent_id = 0
        code = str(uuid.uuid4())
        cur.execute(
            "insert into items (code, type, original_name, parent_id, user_id) values (?, ?, ?, ?, ?)",
            (code, "folder", original_name, parent_id, user_id),
        )
        if cur.rowcount > 0:
            self.connection.commit()
            cur.close()
            logging.info(f"Create folder name '{original_name}' successfully")
            return cur.lastrowid
        else:
            self.connection.rollback()
            cur.close()
            raise Exception(f"Error: folder file name '{original_name}' failed")

    def delete_file(self, original_name):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT id, code, type FROM items WHERE original_name = ?", (original_name,)
        )
        item_id, code, file_type = cur.fetchone()
        if file_type != "file":
            cur.close()
            raise Exception(f"Error: this is not a file")
        file_path = os.path.join(self._root_path, code)
        cur.execute("delete from items where id = ?", (item_id,))
        if cur.rowcount == 1:
            self.connection.commit()
            cur.close()
            os.remove(file_path)
            logging.info(f"Delete file with id '{item_id}' successfully")
            return item_id
        else:
            self.connection.rollback()
            cur.close()
            raise Exception(f"Error: delete item with id '{item_id}' failed")

    def delete_folder(self, original_name):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT id, code, type FROM items WHERE original_name = ?", (original_name,)
        )
        item_id, code, file_type = cur.fetchone()
        if file_type != "folder":
            cur.close()
            raise Exception(f"Error: this is not a folder")
        cur.execute("SELECT count(*) FROM items WHERE parent_id = ?", (item_id,))
        number_children = cur.fetchone()[0]
        if number_children > 0:
            cur.close()
            raise Exception(f"Error: folder has content cannot be deleted")
        cur.execute("delete from items where id = ?", (item_id,))
        if cur.rowcount == 1:
            self.connection.commit()
            cur.close()
            logging.info(f"Delete folder with id '{item_id}' successfully")
            return item_id
        else:
            self.connection.rollback()
            cur.close()
            raise Exception(f"Error: delete item with id '{item_id}' failed")

    def fetch_data(self) -> list[ItemDTO]:
        cur = self.connection.cursor()
        cur.execute(self._fetch_sql)
        rows = cur.fetchall()
        data: list[ItemDTO] = []
        for row in rows:
            data.append(ItemDTO(*row))
        cur.close()
        return data

    def get_item_id_by_name(self, item_name):
        # Connect to the SQLite database
        cur = self.connection.cursor()

        try:
            # Execute the query to find the item ID
            cur.execute("SELECT id FROM items WHERE original_name = ?", (item_name,))
            result = cur.fetchone()

            # Check if a result was found
            if result:
                return result[0]  # Return the item ID
            else:
                logging.info("Item not found.")
                return None
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            return None
        finally:
            # Close the connection
            cur.close()

    def rename_item(self, old_name, new_name):
        if old_name == new_name:
            return

        if not is_valid_filename(new_name) or not is_valid_folder_name(new_name):
            raise Exception("Tên không hợp lệ")

        if self.get_item_id_by_name(new_name) is not None:
            raise Exception("Tên đã tồn tại")

        item_id = self.get_item_id_by_name(old_name)
        if item_id is None:
            raise Exception("Tệp/Thư mục không tồn tại")

        cur = self.connection.cursor()
        cur.execute(
            "UPDATE items SET original_name = ? WHERE id = ?", (new_name, item_id)
        )

        if cur.rowcount == 1:
            self.connection.commit()
            cur.close()
            logging.info(f"Rename item with id '{item_id}' successfully")
        else:
            self.connection.rollback()
            cur.close()
            logging.info(f"Rename item with id '{item_id}' failed")
            raise Exception(f"Cập nhật thất bại")

    def fetch_all_items_based_on_suggestions(self, text):
        """Fetch items from the database that match the input."""
        cur = self.connection.cursor()

        try:
            # Use SQL LIKE to match usernames containing the input text
            cur.execute(
                "SELECT original_name FROM items WHERE original_name LIKE ?", (f"%{text}%",)
            )
            rows = cur.fetchall()

            # Extract usernames from the result
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            return []
        finally:
            cur.close()

    def fetch_items_based_on_suggestions_and_permissions(self, text, username, required_permission=FILE_VIEW):
        """Fetch items from the database that match the input and validate user permissions based on username."""
        cur = self.connection.cursor()

        try:
            # Fetch items based on input text and user permissions using username
            query = FETCH_NAME_FILE_OR_FOLDER_ON_TEXTCHANGED
            cur.execute(query, (f"%{text}%", username, required_permission))
            rows = cur.fetchall()

            # Extract item names from the result
            return [row[0] for row in rows]
        except sqlite3.Error as e:
            logging.error(f"Database error: {e}")
            return []
        finally:
            cur.close()

    def search_tree_iterative(self, search_text: str):
        """
        Perform iterative search on the tree structure, highlighting matching nodes.

        Args:
            search_text (str): The text to search for in the tree.

        Returns:
            list[QModelIndex]: A list of QModelIndex objects for matching nodes.
        """
        search_text = search_text.lower()
        matches = []

        # Start from the root item
        root_index = self.model.index(0, 0)
        if not root_index.isValid():
            logging.warning("Root node is missing.")
            return matches

        stack = [root_index]

        while stack:
            current_index = stack.pop()
            item = self.model.itemFromIndex(current_index)

            if item is None:
                continue

            # Check if the current item's text matches the search text
            if search_text in item.text().lower():
                matches.append(current_index)
                # Set both the foreground (text color) and background color
                item.setForeground(QBrush(Qt.GlobalColor.red))  # Red text color
                item.setBackground(QBrush(QColor(0, 0, 255)))  # Blue background (adjust as needed)
            else:
                item.setForeground(QBrush(Qt.GlobalColor.black))  # Reset text color to black

            # Add children indices to the stack
            for row in range(item.rowCount()):
                stack.append(item.child(row).index())

        return matches

    def clear_item_highlight(self):
        """
        Clear all search highlights in the tree and reset the items to their original state.
        """
        root_index = self.model.index(0, 0)
        stack = [root_index] if root_index.isValid() else []

        while stack:
            index = stack.pop()
            item = self.model.itemFromIndex(index)
            if item:
                # Reset the foreground (text color) to black
                item.setForeground(QBrush(Qt.GlobalColor.black))
                # Reset the background color to white
                item.setBackground(QBrush(Qt.GlobalColor.white))

            # Add children to the stack for further iteration
            for i in range(item.rowCount()):
                stack.append(item.child(i).index())

    def notify_tree_expansion(self):
        """
        Notify the presenter or view to expand the tree view.
        """
        # Trigger a signal or callback to the presenter/view
        if hasattr(self, "on_tree_expansion"):
            self.on_tree_expansion()


if __name__ == "__main__":
    model = ItemModel(
        database_name=r"D:\freelances\Tuan\app_quan_ly_python_qt\app_quan_ly_pyqt6.db"
    )
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.resize(600, 600)
    view = QTreeView()
    view.setModel(model.get_model())
    model.populate_data()
    window.setCentralWidget(view)
    window.show()
    sys.exit(app.exec())
