import os
import pathlib
import time
import uuid
from io import BytesIO

import imagehash
from werkzeug.datastructures import FileStorage
from PIL import Image

image_folder = "./image/"


def set_up_utils():
    if not os.path.isdir(image_folder):
        os.mkdir(image_folder)


def is_valid_image(im: Image):
    try:
        time1 = time.time()
        if im.format == 'GIF':
            return False

        im.load()
        time2 = time.time()
        print(time2 - time1)
        return True
    except Exception:
        return False


def convert_to_webp(im: Image, size=6 * 1024 * 1024, quality=100):
    try:
        print(size)
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


def save(im: Image):
    try:
        name = uuid.uuid4()
        im.save(pathlib.Path(f"{image_folder}{name}.{im.format.lower()}"))
        return name.__str__()
    except Exception as e:
        return None


def delete_image(name):
    if not os.path.isfile(f"{image_folder}{os.path.normpath(name)}.webp"):
        return False
    os.remove(f"{image_folder}{os.path.normpath(name)}.webp")
    return True


def get_image_path(name):
    if not os.path.isfile(f"{image_folder}{os.path.normpath(name)}.webp"):
        return None
    return f"{image_folder}{os.path.normpath(name)}.webp"


def image_hash(im: Image):
    try:
        return bin(int(imagehash.average_hash(im).__str__(), base=16))[2:].zfill(64)
    except Exception as e:
        return None
