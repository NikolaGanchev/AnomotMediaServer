import os

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from extension_type import ExtensionType

media_folder = "./media/"
temp_folder = "./temp/"
media_width = 1080
media_height = 1080


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
