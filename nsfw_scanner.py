import numpy as np
import tensorflow
from PIL import Image
from nsfw_detector import predict
from nsfw_detector.predict import IMAGE_DIM, classify_nd


class NsfwScanner:
    def __init__(self, path):
        self.model = predict.load_model(path)

    def scan_path(self, path):
        return predict.classify(self.model, path)

    def load_images(self, images, image_size):
        """
        Customised image loading function to allow loading pillow images directly
        """
        if isinstance(images, Image.Image):
            images = [images]

        loaded_images = []
        count = 0

        for img in images:
            try:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                if image_size is not None:
                    size_tuple = (image_size[1], image_size[0])
                    if img.size != size_tuple:
                        img = img.resize(size_tuple, Image.NEAREST)

                image = tensorflow.keras.utils.img_to_array(img)
                image /= 255
                loaded_images.append(image)
                count += 1
            except Exception as ex:
                print("Image Load Failure: ", count, ex)

        return np.asarray(loaded_images)

    def scan(self, images, image_dim=IMAGE_DIM):
        images = self.load_images(images, (image_dim, image_dim))
        probs_raw = classify_nd(self.model, images)
        average_probs = {'drawings': probs_raw[0]['drawings'],
                         'hentai': probs_raw[0]['hentai'],
                         'neutral': probs_raw[0]['neutral'],
                         'porn': probs_raw[0]['porn'],
                         'sexy': probs_raw[0]['sexy']}
        max_probs = {'drawings': 0,
                     'hentai': 0,
                     'neutral': 0,
                     'porn': 0,
                     'sexy': 0}
        count = 1
        for prob_raw in probs_raw:
            for stat_name, stat in prob_raw.items():
                average_probs[stat_name] = ((average_probs[stat_name] + stat) * count) / (count + 1)
                max_probs[stat_name] = max(max_probs[stat_name], stat)
        return average_probs, max_probs
