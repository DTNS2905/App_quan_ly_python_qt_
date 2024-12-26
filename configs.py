import logging
import os
import sys
import time
from pathlib import Path
from appdirs import user_data_dir

if getattr(sys, "frozen", True):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS' for accessing bundled files.
    APP_PATH = sys._MEIPASS
    # default files_storage will be saved:
    # C:\Users\<User>\AppData\Local\Phần mềm quản lý hồ sơ công tác\Phần mềm quản lý hồ sơ công tác\1.0.1\files_storage
    FILES_ROOT_PATH = Path(user_data_dir(appname="Phần mềm quản lý hồ sơ công tác", version="1.0.1")) / "files_storage"
    # default logs will be saved:
    # C:\Users\<User>\AppData\Local\Phần mềm quản lý hồ sơ công tác\Phần mềm quản lý hồ sơ công tác\1.0.1\logs
    LOG_PATH = Path(user_data_dir(appname="Phần mềm quản lý hồ sơ công tác", version="1.0.1")) / "logs"

else:
    APP_PATH = os.path.dirname(os.path.abspath(__file__))
    FILES_ROOT_PATH = Path(APP_PATH) / "files_storage"  # Store files locally in the development folder
    LOG_PATH = Path(APP_PATH) / "logs"  # Store logs locally in the development folder

# Database and other paths
DATABASE_NAME = "app_quan_ly_pyqt6.db"
INSTRUCT_PATH = os.path.join(APP_PATH, "README.md")
LOGIN_UI_PATH = Path(APP_PATH) / "ui/login.ui"
DASHBOARD_UI_PATH = Path(APP_PATH) / "ui/admin_dashboard.ui"
REGISTER_UI_PATH = Path(APP_PATH) / "ui/register_ui.ui"
LOG_UI_PATH = Path(APP_PATH) / "ui/log.ui"
PERMISSION_PATH = Path(APP_PATH) / "ui/permission_dialog.ui"
PROFILE_PATH = Path(APP_PATH) / "ui/profile.ui"
ITEM_PERMISSION_PATH = Path(APP_PATH) / "ui/item_permission.ui"
ADD_DEADLINE_PATH = Path(APP_PATH) / "ui/add_deadline.ui"

FILE_TREE_VIEW_COLUMNS = [
    "Tên",
    "Loại",
    "Ngày Tạo",
    "Người Tạo",
    "Thời gian bắt đầu",
    "Thời gian kết thúc",
    "Người giao việc",
    "Người được giao",
]
TIMEZONE = "Asia/Bangkok"

# Ensure directories exist
os.makedirs(LOG_PATH, exist_ok=True)
os.makedirs(FILES_ROOT_PATH, exist_ok=True)


def setup_logging():
    log_filename = os.path.join(LOG_PATH, f"app_log_{time.strftime('%Y-%m-%d')}.log")
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
