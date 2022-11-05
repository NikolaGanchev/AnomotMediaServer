import os
import uuid

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app_utils import get_file_size, max_file_size, file_folder


class FileHandler:
    def __init__(self, file: FileStorage):
        self.file = file

    def in_size_limit(self):
        size = get_file_size(self.file)

        if size > max_file_size or size < 0:
            return False

        return True

    def save(self):
        return save_file(self.file)


def save_file(file: FileStorage):
    name = uuid.uuid4()
    file.save(f"{file_folder}{name}")
    return name


def delete_file(name):
    print(name)
    print(f"{file_folder}{name}")
    if not os.path.isfile(f"{file_folder}{name}"):
        return False
    os.remove(f"{file_folder}{secure_filename(name)}")
    return True


def get_file_path(name):
    if not os.path.isfile(f"{file_folder}{secure_filename(name)}"):
        return None
    return f"{file_folder}{secure_filename(name)}"

