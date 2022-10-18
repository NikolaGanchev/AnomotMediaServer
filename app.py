from PIL import Image
from flask import Flask, request, send_file

from image_utils import is_valid_image, convert_to_webp, save, set_up_utils, save_webp_io, get_image_path, image_hash

app = Flask(__name__)

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
    if file and is_valid_image(Image.open(file)):
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
    img = convert_to_webp(Image.open(file))
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
    name = save(Image.open(file))
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
    img = convert_to_webp(Image.open(file))
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
    f = get_image_path(name)
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
    hash = image_hash(Image.open(file))
    if hash is None:
        return app.response_class(
            status=415
        )
    return str(hash)


if __name__ == '__main__':
    app.run()
