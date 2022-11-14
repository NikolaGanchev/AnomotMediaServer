import os
import unittest

from werkzeug.datastructures import FileStorage

from image_utils import ImageHandler


class ImageTest(unittest.TestCase):
    def test_jpg_is_correct(self):
        file = open_as_werkzeug('test_media/test.jpg')
        ih = ImageHandler(file)
        self.assertTrue(ih.is_valid())
        file.close()

    def test_jpeg_is_correct(self):
        file = open_as_werkzeug('test_media/test.jpeg')
        ih = ImageHandler(file)
        self.assertTrue(ih.is_valid())
        file.close()

    def test_png_is_correct(self):
        file = open_as_werkzeug('test_media/test.png')
        ih = ImageHandler(file)
        self.assertTrue(ih.is_valid())
        file.close()

    def test_webp_is_correct(self):
        file = open_as_werkzeug('test_media/test.webp')
        ih = ImageHandler(file)
        self.assertTrue(ih.is_valid())
        file.close()

    def test_heif_is_correct(self):
        file = open_as_werkzeug('test_media/test.heif')
        ih = ImageHandler(file)
        self.assertTrue(ih.is_valid())
        file.close()

    def test_heic_is_correct(self):
        file = open_as_werkzeug('test_media/test.heic')
        ih = ImageHandler(file)
        self.assertTrue(ih.is_valid())
        file.close()

    def test_jpg_is_incorrect(self):
        file = open_as_werkzeug('test_media/test_invalid.jpg')
        ih = ImageHandler(file)
        self.assertFalse(ih.is_valid())
        file.close()

    def test_png_is_incorrect(self):
        file = open_as_werkzeug('test_media/test_invalid.png')
        ih = ImageHandler(file)
        self.assertFalse(ih.is_valid())
        file.close()

    def test_webp_is_incorrect(self):
        file = open_as_werkzeug('test_media/test_invalid.webp')
        ih = ImageHandler(file)
        self.assertFalse(ih.is_valid())
        file.close()

    def test_heif_is_incorrect(self):
        file = open_as_werkzeug('test_media/test_invalid.heif')
        ih = ImageHandler(file)
        self.assertFalse(ih.is_valid())
        file.close()

    def test_heic_is_incorrect(self):
        file = open_as_werkzeug('test_media/test_invalid.heic')
        ih = ImageHandler(file)
        self.assertFalse(ih.is_valid())
        file.close()

    def test_unknown_extension_is_incorrect(self):
        file = open_as_werkzeug('test_media/test.txt')
        ih = ImageHandler(file)
        self.assertFalse(ih.is_valid())
        file.close()


def open_as_werkzeug(path):
    file = open(path, 'rb')
    return FileStorage(file)


if __name__ == '__main__':
    unittest.main()
