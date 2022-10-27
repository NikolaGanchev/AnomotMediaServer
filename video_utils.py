import json
import os
import pathlib
import subprocess
import tempfile
import uuid
from werkzeug.datastructures import FileStorage

from app_utils import media_folder, media_width, media_height, temp_folder, get_extension, allowed_video_formats, \
    allowed_video_extensions, allowed_video_formats_extensions


def is_valid_video(file: FileStorage):
    extension = get_extension(file)

    if extension not in allowed_video_extensions:
        return False

    args = ['ffprobe', 'pipe:', '-show_entries', 'format=format_name,format_long_name', '-show_streams', '-of', 'json']
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p.communicate(input=file.read())

    if p.returncode != 0:
        return False

    response = json.loads(out.decode('utf-8'))

    is_video = False
    for stream in response['streams']:
        if stream['codec_type'] == 'video':
            if '_pipe' not in response['format']['format_name']:
                is_video = True

    is_allowed_format = False

    for video_format in response['format']['format_name'].split(','):
        if video_format in allowed_video_formats and extension in allowed_video_formats_extensions[video_format]:
            is_allowed_format = True

    return is_video & is_allowed_format


def compress_and_save_video(file: FileStorage, extension):
    name = uuid.uuid4()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.' + extension, dir=temp_folder)
    try:
        file.seek(0)
        tmp.write(file.read())
        print(tmp.name)
        args = ['ffmpeg', '-i', tmp.name,
                "-vf",
                f"scale='if(eq(iw/ih, 1), min({media_width}, iw), if(gt(iw/ih, 1), min({media_width}, iw), -2))':'if(eq(iw/ih, 1), min({media_height}, ih), if(lt(iw/ih, 1), min({media_height}, ih), -2))'",
                '-crf',
                '28',
                '-map',
                '0',
                str(pathlib.Path(f"{media_folder}{name}.mp4"))]
        p = subprocess.Popen(args)
        our, err = p.communicate()

    finally:
        tmp.close()
        os.unlink(tmp.name)

    return str(name)


# TODO
def video_hash(path: os.PathLike):
    return -1
