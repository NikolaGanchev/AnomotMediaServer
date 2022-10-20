import json
import subprocess
from werkzeug.datastructures import FileStorage


def is_valid_video(file: FileStorage):
    args = ['ffprobe', 'pipe:', '-show_format', '-show_streams', '-of', 'json']
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p.communicate(input=file.read())

    if p.returncode != 0:
        return False

    response = json.loads(out.decode('utf-8'))

    print(response)

    for stream in response['streams']:
        if stream['codec_type'] == 'video':
            return True

    return False
