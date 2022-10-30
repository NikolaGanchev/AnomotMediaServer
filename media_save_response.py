import string

from extension_type import ExtensionType


class MediaSaveResponse:
    def __init__(self, media_type: ExtensionType, phash: string, name: string, average_nsfw, max_nsfw):
        self.media_type = media_type
        self.phash = phash
        self.name = name
        self.average_nsfw = average_nsfw
        self.max_nsfw = max_nsfw

    def to_dict(self):
        return {'type': self.media_type.name.lower(), "phash": self.phash, "id": self.name, "avNsfw": self.average_nsfw,
                "maxNsfw": self.max_nsfw}
