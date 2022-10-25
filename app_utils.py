import os
import pathlib
import uuid

from werkzeug.datastructures import FileStorage

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
