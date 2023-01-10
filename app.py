import os

from flask import Flask, request, send_file, jsonify

import virus_scanner
from app_utils import media_folder, temp_folder, get_media_path, delete_media, determine_media_type, \
    get_extension, max_sizes, file_folder
from extension_type import ExtensionType
from file_utils import FileHandler, get_file_path, delete_file
from image_utils import ImageHandler
from media_save_response import MediaSaveResponse
from nsfw_scanner import NsfwScanner
from video_utils import VideoHandler

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = max(max_sizes)


def set_up_utils():
    if not os.path.isdir(media_folder):
        os.mkdir(media_folder)
    if not os.path.isdir(temp_folder):
        os.mkdir(temp_folder)
    if not os.path.isdir(file_folder):
        os.mkdir(file_folder)


set_up_utils()

nsfw_detector = NsfwScanner('./nsfw_model/mobilenet_v2_140_224/saved_model.h5')


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
    should_scan_nsfw = request.args.get('nsfw', type=lambda a: a.lower() == 'true', default=True)
    handler = None

    match media_type:
        case ExtensionType.IMAGE:
            handler = ImageHandler(file)
        case ExtensionType.VIDEO:
            handler = VideoHandler(file)
        case _:
            return app.response_class(
                status=400
            )

    if not handler.in_size_limit():
        return app.response_class(
            status=413
        )

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

    average_nsfw, max_nsfw = None, None

    if should_scan_nsfw:
        if isinstance(handler, VideoHandler):
            handler.init_self_frames(get_media_path(name, media_type))
        average_nsfw, max_nsfw = handler.scan_nsfw(nsfw_detector)

    duration = handler.get_duration()

    del handler

    return jsonify(MediaSaveResponse(media_type, phash, name, average_nsfw, max_nsfw, duration).to_dict()), 201


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
                status=404
            )


@app.route("/file", methods=['POST'])
def save_file_endpoint():
    if 'file' not in request.files:
        return app.response_class(
            status=400
        )

    file = request.files['file']
    if file.filename == '':
        return app.response_class(
            status=400
        )

    handler = FileHandler(file)

    if not handler.in_size_limit():
        return app.response_class(
            status=413
        )

    id = handler.save()

    answer = {'name': file.filename,
              'id': id,
              'threat': virus_scanner.scan_path(f"{file_folder}{id}")}

    return jsonify(answer), 201


@app.route("/file/<name>", methods=['GET'])
def get_file_endpoint(name):
    file = get_file_path(name)

    if file is None:
        return app.response_class(
            status=404
        )

    return send_file(file, mimetype='application/octet-stream')


@app.route("/file/<name>", methods=['DELETE'])
def delete_file_endpoint(name):
    success = delete_file(name)

    if success:
        return app.response_class(
            status=200
        )
    else:
        return app.response_class(
            status=404
        )


@app.route("/image/square", methods=['POST'])
def save_square_image():
    size = int(request.args.get('size'))
    if 'file' not in request.files or size is None or size < 0:
        return app.response_class(
            status=400
        )

    file = request.files['file']
    if file.filename == '':
        return app.response_class(
            status=400
        )

    handler = ImageHandler(file)

    if not handler.in_size_limit():
        return app.response_class(
            status=413
        )

    if not handler.is_valid():
        return app.response_class(
            status=415
        )

    if not handler.is_bigger_or_equal(size, size):
        return app.response_class(
            status=415
        )

    if not handler.get_aspect_ratio() == 1:
        left = int(request.args.get('left'))
        top = int(request.args.get('top'))
        crop_size = int(request.args.get("cropSize"))
        if left is None or top is None or crop_size is None \
                or handler.outside_of_image(left + crop_size, top + crop_size)\
                or left < 0 or top < 0 or crop_size < 0:
            return app.response_class(
                status=400
            )

        handler.crop(left, top, crop_size, crop_size)

    handler.resize(size, size)

    name = handler.save(extension=ExtensionType.IMAGE)

    average_nsfw, max_nsfw = handler.scan_nsfw(nsfw_detector)

    return jsonify({'id': name, 'avgNsfw': average_nsfw})


if __name__ == '__main__':
    from waitress import serve

    serve(app, host='0.0.0.0', port=5000)
