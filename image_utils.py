import os
import pathlib
import uuid
from io import BytesIO

import imagehash
from werkzeug.datastructures import FileStorage
from PIL import Image
from werkzeug.utils import secure_filename

image_folder = "./image/"


def set_up_utils():
    if not os.path.isdir(image_folder):
        os.mkdir(image_folder)


def is_valid_image(file: FileStorage):
    try:
        im = Image.open(file)
        if im.format == 'GIF':
            return False

        im.load()
        return True
    except Exception:
        return False


def convert_to_webp(file: FileStorage, size=6 * 1024 * 1024, quality=100):
    try:
        im = Image.open(file)
        img_io = BytesIO()

        if size > 5 * 1024 * 1024:
            im.thumbnail((1920, 1080))

        im.save(img_io, format='webp', quality=quality, optimise=False)
        img_io.seek(0)
        return img_io
    except Exception as e:
        return None


def save_webp_io(img_io):
    name = uuid.uuid4()
    with open(f"{image_folder}{name}.webp", 'wb') as f:
        f.write(img_io.getbuffer())
    return name.__str__()


def save(file: FileStorage):
    try:
        im = Image.open(file)
        name = uuid.uuid4()
        im.save(pathlib.Path(f"{image_folder}{name}.{im.format.lower()}"))
        return name.__str__()
    except Exception as e:
        return None


def delete_image(name):
    if not os.path.isfile(f"{image_folder}{secure_filename(name)}.webp"):
        return False
    os.remove(f"{image_folder}{secure_filename(name)}.webp")
    return True


def get_image_path(name):
    if not os.path.isfile(f"{image_folder}{secure_filename(name)}.webp"):
        return None
    return f"{image_folder}{secure_filename(name)}.webp"


def image_hash(file: FileStorage):
    try:
        im = Image.open(file)
        return bin(int(imagehash.average_hash(im).__str__(), base=16))[2:].zfill(64)
    except Exception as e:
        return None
