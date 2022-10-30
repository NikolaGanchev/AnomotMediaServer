import pathlib
import uuid
from io import BytesIO

import imagehash
from werkzeug.datastructures import FileStorage
from PIL import Image
from pillow_heif import register_heif_opener

from app_utils import media_folder, media_width, media_height, get_extension, allowed_image_formats, \
    allowed_image_extensions, allowed_image_formats_extensions
from extension_type import ExtensionType

register_heif_opener()


def is_valid_image(file: FileStorage):
    try:
        extension = get_extension(file)

        if extension not in allowed_image_extensions:
            return False

        im = Image.open(file)

        if not im.format.lower() in allowed_image_formats or \
                extension not in allowed_image_formats_extensions[im.format.lower()]:
            return False

        im.load()
        return True
    except Exception:
        return False


def compress_image(file: FileStorage, size=6 * 1024 * 1024, quality=100):
    try:
        im = Image.open(file)
        img_io = BytesIO()

        if not (im.width < media_width and im.height < media_height):
            aspect_ratio = im.width / im.height
            if aspect_ratio > 1:
                im.thumbnail((round(aspect_ratio * media_width), media_height))
            elif aspect_ratio < 1:
                im.thumbnail((media_width, round(aspect_ratio * media_height)))
            else:
                im.thumbnail(media_width, media_height)

        im.save(img_io, format='webp', quality=quality, optimise=True)
        img_io.seek(0)
        return img_io
    except Exception as e:
        return None


def save_webp_io(img_io):
    name = uuid.uuid4()
    with open(f"{media_folder}{name}.{ExtensionType.IMAGE.value}", 'wb') as f:
        f.write(img_io.getbuffer())
    return name.__str__()


def save(file: FileStorage):
    try:
        im = Image.open(file)
        name = uuid.uuid4()
        im.save(pathlib.Path(f"{media_folder}{name}.{ExtensionType.IMAGE.value}"))
        return name.__str__()
    except Exception as e:
        return None


def image_hash(file: FileStorage):
    try:
        im = Image.open(file)
        return bin(int(imagehash.phash(im).__str__(), base=16))[2:].zfill(64)
    except Exception as e:
        return None
