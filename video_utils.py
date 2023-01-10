import json
import os
import pathlib
import subprocess
import tempfile
import uuid
import random

from scenedetect import detect, ContentDetector
import cv2
from PIL import Image
from werkzeug.datastructures import FileStorage

import videohash
from app_utils import media_folder, media_width, media_height, temp_folder, get_extension, allowed_video_formats, \
    allowed_video_extensions, allowed_video_formats_extensions, get_file_size, max_video_size
from nsfw_scanner import NsfwScanner
import time


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
                if get_extension(self.file) in allowed_video_formats_extensions['matroska']:
                    hms_time_str = stream['tags']['DURATION']
                    h, m, s = hms_time_str.split(':')
                    duration += float(h) * 3600 + float(m) * 60 + float(s)
                else:
                    duration += float(stream['duration'])

        return round(duration, 2)

    def is_valid(self):
        self.init_ffprobe()
        return self.file is not None and is_valid_video(self.file, self.ffprobe)

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
        result = scan_nsfw(self.frames, nsfw_scanner)
        self.frames = None
        return result


def ffprobe(file: FileStorage):
    args = ['ffprobe', 'pipe:', '-show_entries', 'format=format_name,format_long_name', '-show_streams', '-of', 'json']
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
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
        args = ['ffmpeg', '-i', tmp.name,
                "-vf",
                f"scale='if(eq(iw/ih, 1), min({media_width}, iw), if(gt(iw/ih, 1), min({media_width}, iw), -2))':'if("
                f"eq(iw/ih, 1), min({media_height}, ih), if(lt(iw/ih, 1), min({media_height}, ih), -2))'"
                f",fps='if(gt(source_fps,30), 30, source_fps)'",
                '-crf',
                '28',
                '-map',
                '0',
                '-map',
                '-0:d',
                str(pathlib.Path(f"{media_folder}{name}.mp4"))]
        p = subprocess.Popen(args)
        p.communicate()

    finally:
        tmp.close()
        os.unlink(tmp.name)

    return str(name)


def get_frames(path):
    scenes = get_scenes(path)

    frames_per_scene = 3

    if len(scenes) > 30:
        frames_per_scene = 2
    elif len(scenes) > 60:
        frames_per_scene = 1

    frames = []

    for i, scene in enumerate(scenes):
        frames.extend(random.sample(range(scene[0].get_frames(), scene[1].get_frames()), frames_per_scene))

    vidcap = cv2.VideoCapture(path)
    success, image = vidcap.read()
    count = 0
    images = []

    for frame in frames:
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        success, image = vidcap.read()
        if success:
            images.append(image)
        count += 1

    return images


def get_scenes(path):
    scene_list = detect(path, ContentDetector(), show_progress=True, start_in_scene=True)
    return scene_list

def video_hash(frames):
    return videohash.video_hash(frames)


def scan_nsfw(frames, nsfw_scanner: NsfwScanner):
    images = [Image.fromarray(x) for x in frames]
    return nsfw_scanner.scan(images)
