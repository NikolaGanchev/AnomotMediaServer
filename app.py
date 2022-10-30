import os
import pathlib

from flask import Flask, request, send_file, jsonify

from app_utils import get_file_size, media_folder, temp_folder, get_media_path, delete_media, determine_media_type, \
    get_extension
from extension_type import ExtensionType
from image_utils import is_valid_image, compress_image, save, save_webp_io, image_hash, ImageHandler
from media_save_response import MediaSaveResponse
from video_utils import is_valid_video, compress_and_save_video, video_hash, VideoHandler

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 70 * 1024 * 1024


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
        return send_file(f, mimetype='video/mp4')


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


@app.route("/media", methods=['POST'])
def save_media_endpoint():
    if 'file' not in request.files:
        return app.response_class(
            status=400
        )

    file = request.files['file']
    if file.filename == '':
        return app.response_class(
            status=400
        )

    extension = get_extension(file)
    media_type = determine_media_type(extension)
    should_hash = request.args.get('phash', type=lambda a: a.lower() == 'true', default=True)
    handler = None

    match media_type:
        case ExtensionType.IMAGE:
            handler = ImageHandler(file)
        case ExtensionType.VIDEO:
            handler = VideoHandler(file)

    if not handler.is_valid():
        return app.response_class(
            status=415
        )

    name = handler.save(extension=extension)
    if name is None:
        return app.response_class(
            status=415
        )

    phash = None
    if should_hash:
        phash = handler.phash(get_media_path(name, media_type))
        if phash is None:
            return app.response_class(
                status=415
            )

    return jsonify(MediaSaveResponse(media_type, phash, name).to_dict()), 201


@app.route("/media/<name>", methods=['GET'])
def get_media_endpoint(name):
    f_video = get_media_path(name, ExtensionType.VIDEO)
    f_image = get_media_path(name, ExtensionType.IMAGE)
    if f_video is None and f_image is None:
        return app.response_class(
            status=404
        )
    else:
        if f_image is not None and f_video is None:
            return send_file(f_image, mimetype='image/webp')
        elif f_video is not None and f_image is None:
            return send_file(f_video, mimetype='video/mp4')
        else:
            # This really shouldn't happen (two files with the same name) and the server should be notified about it
            return app.response_class(
                status=500
            )


@app.route("/media/<name>", methods=['DELETE'])
def delete_media_endpoint(name):
    f_video = get_media_path(name, ExtensionType.VIDEO)
    f_image = get_media_path(name, ExtensionType.IMAGE)
    if f_video is None and f_image is None:
        return app.response_class(
            status=404
        )
    else:
        success = False
        if f_image is not None and f_video is None:
            success = delete_media(name, ExtensionType.IMAGE)
        elif f_video is not None and f_image is None:
            success = delete_media(name, ExtensionType.VIDEO)
        else:
            # This really shouldn't happen (two files with the same name) and the server should be notified about it
            return app.response_class(
                status=500
            )

        if success:
            return app.response_class(
                status=200
            )
        else:
            return app.response_class(
                status=5404
            )


if __name__ == '__main__':
    app.run()
