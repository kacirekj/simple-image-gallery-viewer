import urllib.parse
from datetime import datetime
from pathlib import Path

from bottle import abort, template

from .constant import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from .model import MediaInfo, MediaType


class Utils:
    @staticmethod
    def inline_include(file, **kwargs):
        return template(file, Utils=Utils, **kwargs)

    @staticmethod
    def is_image_file(path: Path) -> bool:
        return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS

    @staticmethod
    def is_video_file(path: Path) -> bool:
        return path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS

    @staticmethod
    def is_media_file(path: Path) -> bool:
        return Utils.is_image_file(path) or Utils.is_video_file(path)

    @staticmethod
    def get_media_type(path: Path) -> MediaType:
        if Utils.is_image_file(path):
            return MediaType.IMAGE

        if Utils.is_video_file(path):
            return MediaType.VIDEO

        raise ValueError(f"Unsupported media file: {path}")

    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def year_month_label(year_month: str) -> str:
        date = datetime.strptime(year_month, "%Y-%m")
        return date.strftime("%Y %B")

    @staticmethod
    def create_media_info(path: Path) -> MediaInfo:
        stat = path.stat()

        created_time = Utils.format_timestamp(
            stat.st_birthtime if hasattr(stat, "st_birthtime") else stat.st_ctime
        )
        modified_time = Utils.format_timestamp(stat.st_mtime)
        media_time = min(created_time, modified_time)

        return MediaInfo(
            path=path,
            media_url="/api/media?filepath=" + urllib.parse.quote(str(path), safe="/"),
            media_type=Utils.get_media_type(path),
            created_time=created_time,
            modified_time=modified_time,
            media_time=media_time,
        )

    @staticmethod
    def create_media_infos(directory: Path) -> list[MediaInfo]:
        paths = [path for path in directory.rglob("*") if Utils.is_media_file(path)]

        if len(paths) > 100000:
            abort(400, "Too many files in directory - have you made a mistake?")

        media_infos = [Utils.create_media_info(path) for path in paths]
        media_infos.sort(key=lambda media_info: media_info.media_time, reverse=True)

        return media_infos

    @staticmethod
    def create_groups(media_infos: list[MediaInfo]) -> dict[str, list[MediaInfo]]:
        result = {}

        for media_info in media_infos:
            year_month = media_info.media_time[:7]

            if year_month not in result:
                result[year_month] = []

            result[year_month].append(media_info)

        return result