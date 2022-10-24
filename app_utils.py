from werkzeug.datastructures import FileStorage

media_folder = "./media/"


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
