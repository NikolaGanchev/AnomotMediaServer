import os

from flask import Flask, request, send_file

from app_utils import get_file_size, media_folder, temp_folder, get_media_path, delete_media
from extension_type import ExtensionType
from image_utils import is_valid_image, compress_image, save, save_webp_io, image_hash
from video_utils import is_valid_video, compress_and_save_video

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


def set_up_utils():
    if not os.path.isdir(media_folder):
        os.mkdir(media_folder)
    if not os.path.isdir(temp_folder):
        os.mkdir(temp_folder)


set_up_utils()


@app.route('/image/valid', methods=['POST'])
def is_valid_image_endpoint():
    if 'file' not in request.files:
        return app.response_class(
            status=415
        )
    file = request.files['file']
    if file.filename == '':
        return app.response_class(
            status=415
        )
    if file and is_valid_image(file):
        return app.response_class(
            status=200
        )
    else:
        return app.response_class(
            status=415
        )


@app.route('/image/convert/webp', methods=['POST'])
def convert_to_webp_endpoint():
    if 'file' not in request.files:
        return app.response_class(
            status=415
        )
    file = request.files['file']
    if file.filename == '':
        return app.response_class(
            status=415
        )

    size = get_file_size(file)
    if not size == -1:
        img = compress_image(file, size)
    else:
        img = compress_image(file)

    if img is None:
        return app.response_class(
            status=415
        )
    else:
        return send_file(img, mimetype='image/webp')


@app.route('/image/save', methods=['POST'])
def save_image_endpoint():
    if 'file' not in request.files:
        return app.response_class(
            status=415
        )
    file = request.files['file']
    if file.filename == '':
        return app.response_class(
            status=415
        )
    name = save(file)
    if name is None:
        return app.response_class(
            status=415
        )
    else:
        return app.response_class(
            name,
            status=201
        )


@app.route("/image/convert/save", methods=['POST'])
def convert_and_save_image():
    if 'file' not in request.files:
        return app.response_class(
            status=415
        )
    file = request.files['file']
    if file.filename == '':
        return app.response_class(
            status=415
        )

    size = get_file_size(file)
    if not size == -1:
        img = compress_image(file, size)
    else:
        img = compress_image(file)

    if img is None:
        return app.response_class(
            status=415
        )
    name = save_webp_io(img)
    if name is None:
        return app.response_class(
            status=415
        )
    else:
        return app.response_class(
            name,
            status=201
        )


@app.route("/image/<name>", methods=['GET'])
def get_image_endpoint(name):
    f = get_media_path(name, ExtensionType.IMAGE)
    if f is None:
        return app.response_class(
            status=404
        )
    else:
        return send_file(f, mimetype='image/webp')


@app.route("/image/hash", methods=['POST'])
def phash_image_endpoint():
    if 'file' not in request.files:
        return app.response_class(
            status=415
        )
    file = request.files['file']
    if file.filename == '':
        return app.response_class(
            status=415
        )
    phash = image_hash(file)
    if phash is None:
        return app.response_class(
            status=415
        )
    return str(phash)


@app.route("/image/<name>", methods=['DELETE'])
def delete_image_endpoint(name):
    f = delete_media(name, ExtensionType.IMAGE)
    if f:
        return app.response_class(
            status=200
        )
    else:
        return app.response_class(
            status=404
        )


@app.route("/video/<name>", methods=['DELETE'])
def delete_video_endpoint(name):
    f = delete_media(name, ExtensionType.VIDEO)
    if f:
        return app.response_class(
            status=200
        )
    else:
        return app.response_class(
            status=404
        )


@app.route("/video/<name>", methods=['GET'])
def get_video_endpoint(name):
    f = get_media_path(name, ExtensionType.VIDEO)
    if f is None:
        return app.response_class(
            status=404
        )
    else:
        return send_file(f, mimetype='image/webp')


@app.route("/video/valid", methods=['POST'])
def is_valid_video_endpoint():
    if 'file' not in request.files:
        return app.response_class(
            status=415
        )
    file = request.files['file']
    if file.filename == '':
        return app.response_class(
            status=415
        )
    if is_valid_video(file):
        return app.response_class(
            status=200
        )
    else:
        return app.response_class(
            status=415
        )


@app.route("/video/compress/save", methods=['POST'])
def compress_and_save_video_endpoint():
    if 'file' not in request.files:
        return app.response_class(
            status=415
        )
    file = request.files['file']
    if file.filename == '':
        return app.response_class(
            status=415
        )
    name = compress_and_save_video(file)
    if name is None:
        return app.response_class(
            status=415
        )
    else:
        return app.response_class(
            name,
            status=201
        )


if __name__ == '__main__':
    app.run()
