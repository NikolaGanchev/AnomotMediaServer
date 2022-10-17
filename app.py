from flask import Flask, request, redirect, flash, send_file

from utils import is_valid_image, convert_to_webp

app = Flask(__name__)


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
    img = convert_to_webp(file)
    if img is None:
        return app.response_class(
            status=415
        )
    else:
        return send_file(img, mimetype='image/webp')


if __name__ == '__main__':
    app.run()
