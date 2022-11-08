import string

from extension_type import ExtensionType


class MediaSaveResponse:
    def __init__(self, media_type: ExtensionType, phash: string, name: string, average_nsfw, max_nsfw, duration):
        self.media_type = media_type
        self.phash = phash
        self.name = name
        self.average_nsfw = average_nsfw
        self.max_nsfw = max_nsfw
        self.duration = duration

    def to_dict(self):
        response = {'type': self.media_type.name.lower(),
                    "phash": self.phash,
                    "id": self.name,
                    "avNsfw": self.average_nsfw}

        if self.max_nsfw is not None:
            response["maxNsfw"] = self.max_nsfw

        if self.duration is not None:
            response["duration"] = self.duration

        return response
