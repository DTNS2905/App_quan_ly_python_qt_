import logging
import os.path
import shutil
import sqlite3
import sys
import traceback
import uuid
from dataclasses import dataclass

from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QFileIconProvider

from common import session
from common.file import get_file_type
from common.model import NativeSqlite3Model
from common.time import convert_utc_time_to_timezone
from configs import DATABASE_NAME, FILES_ROOT_PATH, FILE_TREE_VIEW_COLUMNS, TIMEZONE
from messages.permissions import FILE_VIEW, FOLDER_VIEW
from sql_statements.item import (
    CREATE_ITEM_TABLE_SQL,
    CREATE_PERMISSION_USER_ITEM_TABLE_SQL,
    INIT_DATA,
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


def build_tree(items: list[ItemDTO]):
    item_dict = {item.id: item for item in items}
    root_node = []
    for item in items:
        if item.parent_id == -1:
            root_node = item
        else:
            parent = item_dict[item.parent_id]
            if not hasattr(parent, "children"):
                parent.children = []
            parent.children.append(item)

    return root_node


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

    def populate_data(self):
        items = self.fetch_data()
        root_item_data = build_tree(items)
        font_size = 14

        # Initialize QFileIconProvider
        icon_provider = QFileIconProvider()

        # Get the root folder icon
        root_icon = icon_provider.icon(QFileIconProvider.IconType.Folder)
        root_node = CustomItem(root_item_data.original_name, font_size, True)
        root_node.set_custom_icon(root_icon)

        def traverse(parent_node: CustomItem, parent_data: ItemDTO, f_size):
            for index, child in enumerate(getattr(parent_data, "children", [])):
                try:
                    permission = FOLDER_VIEW if child.type == "folder" else FILE_VIEW
                    if (
                        child.original_name != "root"
                        and not session.SESSION.match_permissions(permission)
                        and not session.SESSION.match_item_permissions(
                            child.original_name, permission
                        )
                    ):
                        continue

                    icon = icon_provider.icon(
                        QFileIconProvider.IconType.Folder
                        if child.type == "folder"
                        else QFileIconProvider.IconType.File
                    )
                    item = CustomItem(
                        child.original_name, f_size - 1, child.type == "folder"
                    )
                    item.set_custom_icon(icon)
                    item_type = CustomItem(
                        get_file_type(child.original_name),
                        f_size - 1,
                        child.type == "folder",
                    )
                    created_at = convert_utc_time_to_timezone(
                        child.created_at, TIMEZONE
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    item_created_at = CustomItem(
                        created_at, f_size - 1, child.type == "folder"
                    )
                    cur = self.connection.cursor()
                    cur.execute(
                        "SELECT fullname FROM profiles WHERE user_id = ?",
                        (child.user_id,),
                    )
                    fullname = cur.fetchone()[0]
                    item_created_by = CustomItem(
                        fullname, f_size - 1, child.type == "folder"
                    )
                    parent_node.setChild(index, 0, item)
                    parent_node.setChild(index, 1, item_type)
                    parent_node.setChild(index, 2, item_created_at)
                    parent_node.setChild(index, 3, item_created_by)
                    traverse(item, child, f_size - 1)
                except:
                    logging.error(traceback.print_exc())

        traverse(root_node, root_item_data, font_size)
        self.get_root_node().appendRow(root_node)

    def refresh_model(self):
        self.model = QStandardItemModel(0, len(FILE_TREE_VIEW_COLUMNS))
        self.model.setHorizontalHeaderLabels(FILE_TREE_VIEW_COLUMNS)
        self.populate_data()
        return self.model

    def get_root_path(self):
        return self._root_path

    def create_file(
        self, username: str, file_path: str, parent_original_name: str = None
    ):
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
        original_name = os.path.basename(file_path)
        code = str(uuid.uuid4())
        cur.execute(
            "insert into items (code, type, original_name, parent_id, user_id) values (?, ?, ?, ?, ?)",
            (code, "file", original_name, parent_id, user_id),
        )
        if cur.rowcount > 0:
            self.connection.commit()
            cur.close()
            shutil.copy(file_path, os.path.join(self._root_path, code))
            logging.info(f"Create file name '{original_name}' successfully")
            return cur.lastrowid
        else:
            self.connection.rollback()
            cur.close()
            raise Exception(f"Error: create file name '{original_name}' failed")

    def open_file(self, original_name):
        cur = self.connection.cursor()
        cur.execute(
            "SELECT id, code, type FROM items WHERE original_name = ?", (original_name,)
        )
        item_id, code, file_type = cur.fetchone()
        file_path = os.path.join(self._root_path, code)
        if file_type != "file":
            return

        # Open the file using the default application based on the platform
        if sys.platform.startswith("win32"):
            os.startfile(file_path)  # Windows
        elif sys.platform.startswith("darwin"):
            os.system(f'Open "{file_path}"')  # macOS
        else:
            os.system(f'open "{file_path}"')  # Linux

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
        self, username: str, original_name: str, parent_original_name: str = None
    ):
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
