import os
import unittest

from werkzeug.datastructures import FileStorage

from image_utils import ImageHandler
from video_utils import VideoHandler


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


class VideoTest(unittest.TestCase):
    def test_mp4_is_correct(self):
        file = open_as_werkzeug('test_media/test.mp4')
        video = VideoHandler(file)
        self.assertTrue(video.is_valid())
        file.close()

    def test_mkv_is_correct(self):
        file = open_as_werkzeug('test_media/test.mkv')
        video = VideoHandler(file)
        self.assertTrue(video.is_valid())
        file.close()

    def test_mov_is_correct(self):
        file = open_as_werkzeug('test_media/test.mov')
        video = VideoHandler(file)
        self.assertTrue(video.is_valid())
        file.close()

    def test_unknown_extension_is_incorrect(self):
        file = open_as_werkzeug('test_media/test.txt')
        video = VideoHandler(file)
        self.assertFalse(video.is_valid())
        file.close()

    def test_mp4_duration_is_correct(self):
        file = open_as_werkzeug('test_media/test.mp4')
        video = VideoHandler(file)
        self.assertAlmostEqual(round(video.get_duration()), 25)
        file.close()

    def test_mkv_duration_is_correct(self):
        file = open_as_werkzeug('test_media/test.mkv')
        video = VideoHandler(file)
        self.assertAlmostEqual(round(video.get_duration()), 25)
        file.close()

    def test_mov_duration_is_correct(self):
        file = open_as_werkzeug('test_media/test.mov')
        video = VideoHandler(file)
        self.assertAlmostEqual(round(video.get_duration()), 25)
        file.close()


def open_as_werkzeug(path):
    file = open(path, 'rb')
    return FileStorage(file)


if __name__ == '__main__':
    unittest.main()
