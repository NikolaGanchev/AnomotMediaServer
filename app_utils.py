import os

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from extension_type import ExtensionType


allowed_image_formats = ['png', 'jpeg', 'tiff', 'bmp', 'webp', 'heif', 'heic']
allowed_video_formats = ['mov', 'mp4', 'matroska']

allowed_image_extensions = ['png', 'jpg', 'tiff', 'bmp', 'webp', 'heif', 'heic']
allowed_video_extensions = ['mov', 'mp4', 'mkv']

allowed_image_formats_extensions = {'png': 'png', 'jpeg': 'jpg', 'tiff': 'tiff', 'bmp': 'bmp', 'webp': 'webp',
                                    'heif': ['heif', 'heic']}
allowed_video_formats_extensions = {'mov': 'mov', 'mp4': 'mp4', 'matroska': 'mkv'}

max_image_size = 10 * 1024 * 1024
max_video_size = 70 * 1024 * 1024
max_file_size = 5 * 1024 * 1024

max_sizes = [max_image_size, max_video_size]

media_folder = "./media/"
file_folder = "./files/"
temp_folder = "./temp/"
media_width = 1080
media_height = 1080


# Returns the file size in bytes
def get_file_size(file: FileStorage):
    try:
        current_position = file.tell()
        # seek the end of the file
        file.seek(0, 2)
        size = file.tell()
        file.seek(current_position)
        return size
    except Exception as e:
        return -1


def get_extension(file: FileStorage):
    filename, file_extension = os.path.splitext(file.filename)
    return file_extension[1:]  # remove the dot in the extension


def delete_media(name, media_type: ExtensionType):
    if not os.path.isfile(f"{media_folder}{secure_filename(name)}.{media_type.value}"):
        return False
    os.remove(f"{media_folder}{secure_filename(name)}.{media_type.value}")
    return True


def get_media_path(name, media_type: ExtensionType):
    if not os.path.isfile(f"{media_folder}{secure_filename(name)}.{media_type.value}"):
        return None
    return f"{media_folder}{secure_filename(name)}.{media_type.value}"


def determine_media_type(extension):
    if extension in allowed_image_extensions:
        return ExtensionType.IMAGE
    elif extension in allowed_video_extensions:
        return ExtensionType.VIDEO
    else:
        return None
