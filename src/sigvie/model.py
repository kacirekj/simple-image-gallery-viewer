from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class MediaType(Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


@dataclass(frozen=True)
class MediaInfo:
    path: Path
    media_url: str
    media_type: MediaType
    created_time: str
    modified_time: str
    media_time: str