import logging
import os
import time
from pathlib import Path

DATABASE_NAME = "app_quan_ly_pyqt6.db"
FILES_ROOT_PATH = Path(__file__).parent / 'files_storage'
LOGIN_UI_PATH = Path(__file__).parent / 'ui/login.ui'
DASHBOARD_UI_PATH = Path(__file__).parent / 'ui/admin_dashboard.ui'
REGISTER_UI_PATH = Path(__file__).parent / 'ui/register_ui.ui'
FILE_TREE_VIEW_COLUMNS = ["Tên", "Loại", "Ngày Tạo", "Người Tạo"]
LOG_PATH = Path(__file__).parent / 'logs'
os.makedirs(LOG_PATH, exist_ok=True)


def setup_logging():
    log_filename = os.path.join(LOG_PATH, f"app_log_{time.strftime('%Y-%m-%d')}.log")
    logging.basicConfig(filename=log_filename, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
