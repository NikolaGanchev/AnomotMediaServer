import json
import pathlib
import subprocess
import uuid

import ffmpeg
from werkzeug.datastructures import FileStorage

from app_utils import media_folder

allowed_video_formats = ['mov', 'mp4']


def is_valid_video(file: FileStorage):
    args = ['ffprobe', 'pipe:', '-show_entries', 'format=format_name,format_long_name', '-show_streams', '-of', 'json']
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p.communicate(input=file.read())

    if p.returncode != 0:
        return False

    response = json.loads(out.decode('utf-8'))

    is_video = False
    for stream in response['streams']:
        if stream['codec_type'] == 'video':
            if not '_pipe' in response['format']['format_name']:
                is_video = True

    is_allowed_format = False

    for video_format in response['format']['format_name'].split(','):
        if video_format in allowed_video_formats:
            is_allowed_format = True

    return is_video & is_allowed_format


def compress_and_save_video(file: FileStorage):
    name = uuid.uuid4()
    process = (
        ffmpeg
        .input('pipe:')
        .output(str(pathlib.Path(f"{media_folder}{name}.mp4")))
        .overwrite_output()
        .run_async(pipe_stdin=True)
    )

    process.communicate(input=file.read())
    return str(name)
