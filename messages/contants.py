from messages.permissions import *

HEADERS_FILE_TREE = ["Tên tài liệu/Thư mục", "Kích cỡ", "Loại tài liệu", "Ngày điều chỉnh"]

PERMISSION_TRANSLATIONS = {
    f"{FILE_VIEW}": "Xem tài liệu",
    f"{FILE_CREATE}": "Tạo tài liệu",
    f"{FILE_RENAME}": "Thay tên tài liệu",
    f"{FILE_DELETE}": "Xóa tài liệu",
    f"{FILE_DOWNLOAD}": "Tải tài liệu ",

    f"{FOLDER_VIEW}": "Xem thư mục",
    f"{FOLDER_CREATE}": "Tạo thư mục",
    f"{FOLDER_RENAME}": "Cập nhật thư mục",
    f"{FOLDER_DELETE}": "Xóa thư mục",

    f"{PERMISSION_VIEW}": "Xem cấp quyền",
    f"{PERMISSION_GRANT}": "Cấp quyền",
    f"{PERMISSION_UNGRANT}": "Thu hồi quyền",
    f"{LOG_VIEW}" : "Xem bảng lịch sử",
    f"{USER_DELETE}": "Xóa người dùng"

    # Add more translations as needed
}

