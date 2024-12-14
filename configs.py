import logging
import os
import sys
import time
from pathlib import Path

if getattr(sys, "frozen", False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    APP_PATH = sys._MEIPASS
else:
    APP_PATH = os.path.dirname(os.path.abspath(__file__))

FILES_ROOT_PATH = os.path.join(APP_PATH, "files_storage")

DATABASE_NAME = "app_quan_ly_pyqt6.db"
INSTRUCT_PATH = Path(__file__).parent / "README.md"
LOG_PATH = Path(__file__).parent / "logs"
LOGIN_UI_PATH = Path(__file__).parent / "ui/login.ui"
DASHBOARD_UI_PATH = Path(__file__).parent / "ui/admin_dashboard.ui"
REGISTER_UI_PATH = Path(__file__).parent / "ui/register_ui.ui"
LOG_UI_PATH = Path(__file__).parent / "ui/log.ui"
PERMISSION_PATH = Path(__file__).parent / "ui/permission_dialog.ui"
PROFILE_PATH = Path(__file__).parent / "ui/profile.ui"
ITEM_PERMISSION_PATH = Path(__file__).parent / "ui/item_permission.ui"
ADD_DEADLINE_PATH = Path(__file__).parent / "ui/add_deadline.ui"
FILE_TREE_VIEW_COLUMNS = [
    "Tên", "Loại", "Ngày Tạo", "Người Tạo", "Thời gian bắt đầu", "Thời gian kết thúc", "Người giao việc",
    "Người được giao"
]
TIMEZONE = "Asia/Bangkok"

os.makedirs(LOG_PATH, exist_ok=True)
os.makedirs(FILES_ROOT_PATH, exist_ok=True)


def setup_logging():
    log_filename = os.path.join(LOG_PATH, f"app_log_{time.strftime('%Y-%m-%d')}.log")
    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
