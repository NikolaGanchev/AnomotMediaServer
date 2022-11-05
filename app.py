import os

from flask import Flask, request, send_file, jsonify

from app_utils import media_folder, temp_folder, get_media_path, delete_media, determine_media_type, \
    get_extension, max_sizes
from extension_type import ExtensionType
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
        average_nsfw, max_nsfw = handler.scan_nsfw(nsfw_detector)

    return jsonify(MediaSaveResponse(media_type, phash, name, average_nsfw, max_nsfw).to_dict()), 201


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


if __name__ == '__main__':
    app.run()
