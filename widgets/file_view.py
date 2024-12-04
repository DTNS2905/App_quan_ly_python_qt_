import sqlite3

from PyQt5.QtCore import Qt
from PyQt6.QtCore import QModelIndex, QAbstractItemModel


class DatabaseItemModel(QAbstractItemModel):
    def __init__(self, database_name, table_name):
        super().__init__()
        self.connection = sqlite3.connect(database_name)
        self._table_name = table_name

    def rowCount(self, parent=QModelIndex()):
        # Implement logic to count rows based on your database query
        cur = self.connection.cursor()
        # if parent is None or not parent.isValid():
        #     print(f"Row count no parent")
        #     cur.execute(f"SELECT COUNT(*) FROM {self._table_name}")
        # else:
        #     print(f"Row count: parent id {parent.internalId()}")
        #     cur.execute(f"SELECT COUNT(*) FROM {self._table_name} WHERE parent_id = ?",
        #                 (parent.internalId(),))

        cur.execute(f"SELECT COUNT(*) FROM {self._table_name}")
        row_count = cur.fetchone()[0]
        print(f"Row count: {row_count}")
        return row_count

    def columnCount(self, parent=QModelIndex()):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {self._table_name}")
        column_count = cursor.description.__len__()
        print(f"Column count: {column_count}")
        return column_count

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            print(f"index.isValid()")
            return None

        row = index.row()
        column = index.column()

        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {self._table_name} LIMIT ?, 1", (row,))

        if role == Qt.DisplayRole:
            item = cursor.fetchone()[column]
            print(f"{row} - {column}: {item}")
            return item

        print(f"{row} - {column}: None")
        return None

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        cursor = self.connection.cursor()
        if not parent.isValid():
            # Root index
            cursor.execute(f"SELECT id FROM {self._table_name} LIMIT ?, 1", (row,))
            return self.createIndex(row, column, cursor.fetchone()[0])

        # # Child index (if applicable, adjust query accordingly)
        # cursor.execute(f"SELECT id FROM {self._table_name} WHERE parent_id = ? LIMIT ?, 1",
        #                (parent.internalId(), row))

        # cursor.execute(f"SELECT id FROM {self._table_name} LIMIT ?, 1", (row,))
        # return self.createIndex(row, column, cursor.fetchone()[0])

        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        return QModelIndex()

        # cursor = self.connection.cursor()
        # cursor.execute(f"SELECT parent_id FROM {self._table_name} WHERE id = ?",
        #                (index.internalId(),))
        # parent_id = cursor.fetchone()[0]
        #
        # if parent_id == 0:
        #     return QModelIndex()  # Root index
        #
        # # Recursive function to find the parent index
        # def find_parent(_parent_id, root_index):
        #     for row in range(self.rowCount(root_index)):
        #         child_index = self.index(row, 0, root_index)
        #         child_id = child_index.internalId()
        #         if child_id == _parent_id:
        #             return child_index
        #         elif self.hasChildren(child_index):
        #             result = find_parent(_parent_id, child_index)
        #             if result.isValid():
        #                 return result
        #     return QModelIndex()
        #
        # # Find the parent index using the recursive function
        # return find_parent(parent_id, self.rootIndex())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable  # Adjust flags as needed
