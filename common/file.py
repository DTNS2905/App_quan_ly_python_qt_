import os


def get_file_type(filename):
    if len(filename.split(".")) == 1:
        return "Thư mục"

    extension = filename.split(".")[-1].lower()

    # Common file types
    image_extensions = ["jpg", "jpeg", "png", "gif", "bmp"]
    document_extensions = ["doc", "docx", "pdf", "txt", "rtf"]
    video_extensions = ["mp4", "avi", "mov", "mkv"]
    audio_extensions = ["mp3", "wav", "ogg", "flac"]

    if extension in image_extensions:
        return "Hình Ảnh"
    elif extension in document_extensions:
        return "Tài liệu"
    elif extension in video_extensions:
        return "Phim Ảnh"
    elif extension in audio_extensions:
        return "Âm Thanh"
    else:
        return "Tệp"


def is_valid_filename(filename):
    # Basic checks
    if not filename:
        return False

    # Check for invalid characters (adjust the pattern as needed)
    invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    if any(char in filename for char in invalid_chars):
        return False

    # Check for reserved names on Windows (if applicable)
    if os.name == "nt" and filename.upper() in ["CON", "PRN", "AUX", "NUL"]:
        return False

    return True


def is_valid_folder_name(folder_name):
    # Basic checks
    if not folder_name:
        return False

    # Check for invalid characters (adjust the pattern as needed)
    invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
    if any(char in folder_name for char in invalid_chars):
        return False

    # Check for reserved names on Windows (if applicable)
    if os.name == "nt" and folder_name.upper() in [
        "SYSTEM VOLUME INFORMATION",
        "PROGRAM FILES",
        "PROGRAM FILES (X86)",
        "WINDOWS",
    ]:
        return False

    return True
