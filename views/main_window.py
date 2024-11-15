from file_tree_view import FileTreeViewWindow


class MainWindow(FileTreeViewWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)