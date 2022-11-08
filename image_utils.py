import pathlib
import uuid
from io import BytesIO

import imagehash
from werkzeug.datastructures import FileStorage
from PIL import Image
from pillow_heif import register_heif_opener

from app_utils import media_folder, media_width, media_height, get_extension, allowed_image_formats, \
    allowed_image_extensions, allowed_image_formats_extensions, get_file_size, max_image_size
from extension_type import ExtensionType
from nsfw_scanner import NsfwScanner

register_heif_opener()


class ImageHandler:
    def __init__(self, file: FileStorage):
        self.file = file

    def in_size_limit(self):
        size = get_file_size(self.file)

        if size > max_image_size or size < 0:
            return False

        return True

    def get_duration(self):
        return None

    def is_valid(self):
        return self.file and is_valid_image(self.file)

    def save(self, extension):
        compressed = compress_image(self.file)
        if compressed is None:
            return None
        return save_webp_io(compressed)

    def phash(self, path):
        return image_hash(path)

    def scan_nsfw(self, nsfw_scanner: NsfwScanner):
        return (nsfw_scanner.scan(Image.open(self.file)))[0], None


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


def image_hash(path):
    try:
        im = Image.open(path)
        return bin(int(imagehash.phash(im).__str__(), base=16))[2:].zfill(64)
    except Exception as e:
        return None
