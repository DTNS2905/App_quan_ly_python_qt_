def get_file_type(filename):
    if len(filename.split('.')) == 1:
        return "Thư mục"

    extension = filename.split('.')[-1].lower()

    # Common file types
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
    document_extensions = ['doc', 'docx', 'pdf', 'txt', 'rtf']
    video_extensions = ['mp4', 'avi', 'mov', 'mkv']
    audio_extensions = ['mp3', 'wav', 'ogg', 'flac']

    if extension in image_extensions:
        return 'Hình Ảnh'
    elif extension in document_extensions:
        return 'Tài liệu'
    elif extension in video_extensions:
        return 'Phim Ảnh'
    elif extension in audio_extensions:
        return 'Âm Thanh'
    else:
        return 'Tệp'
