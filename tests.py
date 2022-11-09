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



def open_as_werkzeug(path):
    file = open(path, 'rb')
    return FileStorage(file)

if __name__ == '__main__':
    unittest.main()
