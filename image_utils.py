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
        self.size = get_file_size(self.file)
        self.im: Image = None
        self.is_valid_image = self.validate()

    def in_size_limit(self):
        if self.size > max_image_size or self.size < 0:
            return False

        return True

    def get_duration(self):
        return None

    def validate(self):
        if self.file is None:
            return False

        try:
            extension = get_extension(self.file)

            if extension not in allowed_image_extensions:
                return False

            self.im = Image.open(self.file)

            if not self.im.format.lower() in allowed_image_formats or \
                    extension not in allowed_image_formats_extensions[self.im.format.lower()]:
                return False

            self.im.load()
            return True
        except Exception:
            self.im = None
            return False

    def is_valid(self):
        return self.is_valid_image

    def crop(self, left: int, top: int, width: int, height: int):
        self.im = self.im.crop((left, top, left + width, top + height))

    def is_bigger_or_equal(self, width: int, height: int):
        return self.im.width >= width and self.im.height >= height

    def outside_of_image(self, x, y):
        if x < 0 or y < 0:
            return True

        return x > self.im.width or y > self.im.height

    def get_aspect_ratio(self):
        return self.im.width / self.im.height

    def resize(self, width, height):
        self.im = self.im.resize((width, height))

    def save(self, extension):
        if not self.is_valid_image:
            return None

        compressed = self.compress_image()
        if compressed is None:
            return None
        return save_webp_io(compressed)

    def compress_image(self, size=6 * 1024 * 1024, quality=100):
        if not self.is_valid_image:
            return None

        try:
            img_io = BytesIO()

            if not (self.im.width < media_width and self.im.height < media_height):
                aspect_ratio = self.im.width / self.im.height
                if aspect_ratio > 1:
                    self.im.thumbnail((round(aspect_ratio * media_width), media_height))
                elif aspect_ratio < 1:
                    self.im.thumbnail((media_width, round(aspect_ratio * media_height)))
                else:
                    self.im.thumbnail(media_width, media_height)

            self.im.save(img_io, format='webp', quality=quality, optimise=True)
            img_io.seek(0)
            return img_io
        except Exception as e:
            return None

    def phash(self, path):
        try:
            return imagehash.phash(Image.open(path)).__str__()
        except Exception as e:
            return None

    def scan_nsfw(self, nsfw_scanner: NsfwScanner):
        return (nsfw_scanner.scan(self.im))[0], None


def save_webp_io(img_io):
    name = uuid.uuid4()
    with open(f"{media_folder}{name}.{ExtensionType.IMAGE.value}", 'wb') as f:
        f.write(img_io.getbuffer())
    return name.__str__()
