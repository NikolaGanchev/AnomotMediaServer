import json
import os
import pathlib
import subprocess
import tempfile
import uuid

import cv2
from PIL import Image
from werkzeug.datastructures import FileStorage

import videohash
from app_utils import media_folder, media_width, media_height, temp_folder, get_extension, allowed_video_formats, \
    allowed_video_extensions, allowed_video_formats_extensions, get_file_size, max_video_size
from nsfw_scanner import NsfwScanner


class VideoHandler:
    def __init__(self, file: FileStorage):
        self.frames = None
        self.file = file
        self.ffprobe = None

    def in_size_limit(self):
        size = get_file_size(self.file)

        if size > max_video_size or size < 0:
            return False

        return True

    def init_ffprobe(self):
        if self.ffprobe is None:
            self.ffprobe = ffprobe(self.file)

    def get_duration(self):
        self.init_ffprobe()

        duration = 0
        for stream in self.ffprobe['streams']:
            if stream['codec_type'] == 'video':
                duration += float(stream['duration'])

        return round(duration, 2)

    def is_valid(self):
        self.init_ffprobe()
        return self.file and is_valid_video(self.file, self.ffprobe)

    def save(self, extension):
        return compress_and_save_video(self.file, extension=extension)

    def init_self_frames(self, path):
        if self.frames is None:
            self.frames = get_frames(path)

    def phash(self, path):
        self.init_self_frames(path)
        return video_hash(self.frames)

    def scan_nsfw(self, nsfw_scanner: NsfwScanner):
        if self.frames is None:
            raise RuntimeError("Frames need to be initialised before calling scan_nsfw")
        return scan_nsfw(self.frames, nsfw_scanner)


def ffprobe(file: FileStorage):
    args = ['ffprobe', 'pipe:', '-show_entries', 'format=format_name,format_long_name', '-show_streams', '-of', 'json']
    p = subprocess.Popen(args, stdout=None, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = p.communicate(input=file.read())

    if p.returncode != 0:
        return None

    return json.loads(out.decode('utf-8'))


def is_valid_video(file: FileStorage, response):
    extension = get_extension(file)

    if extension not in allowed_video_extensions:
        return False

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
                f"scale='if(eq(iw/ih, 1), min({media_width}, iw), if(gt(iw/ih, 1), min({media_width}, iw), -2))':'if("
                f"eq(iw/ih, 1), min({media_height}, ih), if(lt(iw/ih, 1), min({media_height}, ih), -2))'"
                f",fps='if(gt(source_fps,30), 30, source_fps)'",
                '-crf',
                '28',
                '-map',
                '0',
                str(pathlib.Path(f"{media_folder}{name}.mp4"))]
        p = subprocess.Popen(args)
        p.communicate()

    finally:
        tmp.close()
        os.unlink(tmp.name)

    return str(name)


def get_frames(path):
    vidcap = cv2.VideoCapture(path)
    success, image = vidcap.read()
    count = 0
    images = []
    while success:
        success, image = vidcap.read()
        if success:
            images.append(image)
        count += 1

    return images


def video_hash(frames):
    return videohash.video_hash(frames)

def scan_nsfw(frames, nsfw_scanner: NsfwScanner):
    images = [Image.fromarray(x) for x in frames]
    return nsfw_scanner.scan(images)
