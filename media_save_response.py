import string

from extension_type import ExtensionType


class MediaSaveResponse:
    def __init__(self, media_type: ExtensionType, phash: string, name: string):
        self.media_type = media_type
        self.phash = phash
        self.name = name

    def to_dict(self):
        return {'type': self.media_type.name.lower(), "phash": self.phash, "id": self.name}
