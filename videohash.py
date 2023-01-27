import math
import time

import cv2

import imagehash
from PIL import Image

"""
    Custom video hashing algorithm
    Downscales every frame of a video to 16x16, creates a 30 column wide grid, places all frames inside of it and 
    generates a phash of the grid image.
    Provides satisfying similarity detection at a reasonable speed with no collisions found yet.
    Further testing required.
"""


def video_hash(images):
    image = create_hash_image(images)
    return imagehash.phash(image, hash_size=8).__str__()


def create_hash_image(images):
    images = [Image.fromarray(cv2.cvtColor(x, cv2.COLOR_BGR2RGB)).resize((16, 16), Image.ANTIALIAS) for x in images]
    widths, heights = zip(*(i.size for i in images))
    columns = 5
    rows = math.ceil(len(images) / columns)
    total_width = max(widths) * columns
    total_height = max(heights) * rows

    image = Image.new('RGB', (total_width, total_height))

    image_index = 0
    for i in range(rows):
        for j in range(columns):
            image.paste(images[image_index], (j * images[image_index].width, i * images[image_index].height))
            image_index += 1
            if image_index >= len(images):
                break

        if image_index >= len(images):
            break

    return image
