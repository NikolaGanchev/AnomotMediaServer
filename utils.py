from io import BytesIO

from werkzeug.datastructures import FileStorage
from PIL import Image


def is_valid_image(file: FileStorage):
    try:
        im = Image.open(file)

        if im.format == 'GIF':
            return False

        im.load()
        return True
    except Exception:
        return False


def convert_to_webp(file: FileStorage):
    try:
        im = Image.open(file)
        img_io = BytesIO()
        im.save(img_io, format='webp', quality=70, optimise=True)
        img_io.seek(0)
        return img_io
    except Exception as e:
        return None
