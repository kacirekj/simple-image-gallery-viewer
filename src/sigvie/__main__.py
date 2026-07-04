import argparse
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from bottle import abort, request, route, run, static_file, template

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
    ".avif",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".webm",
}

BASE_DIR = Path(__file__).parent


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


class Utils:
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


@route("/api/media")
def serve_media():
    filepath_param = request.query.decode().get("filepath", "").strip()

    if not filepath_param:
        abort(400, "Missing filepath parameter.")

    media_path = Path(filepath_param).expanduser().resolve(strict=False)

    if not Utils.is_media_file(media_path):
        abort(404, f"File does not exist or is not a supported media file: {media_path}")

    file_response = static_file(media_path.name, root=str(media_path.parent))
    file_response.set_header("Cache-Control", "public, max-age=31536000")

    return file_response


@route("/")
@route("/<path:path>")
def index(path: str = ""):
    # Parse

    filepath_param = request.query.decode().get("filepath", "").strip()
    static_path = BASE_DIR / path

    if filepath_param:
        filepath = Path(filepath_param).expanduser().resolve(strict=False)
    else:
        filepath = None

    # Switch

    if path == "" and not filepath_param:

        # Return index.html

        return template(
            "web/page/index.html",
            filepath=filepath_param,
            Utils=Utils,
        )

    elif filepath and filepath.is_dir():

        # Return gallery.html

        directory = filepath
        media_infos = Utils.create_media_infos(directory)
        media_infos_groups = Utils.create_groups(media_infos)

        return template(
            "web/page/gallery.html",
            filepath=filepath_param,
            media_infos_groups=media_infos_groups,
            MediaType=MediaType,
            Utils=Utils,
        )

    elif filepath and filepath.is_file():

        # Return file.html

        media_info = Utils.create_media_info(filepath)

        return template(
            "web/page/file.html",
            filepath=filepath_param,
            media=media_info,
            MediaType=MediaType,
            Utils=Utils,
        )

    elif filepath_param:

        # Return 404 filepath not found

        abort(404, f"Directory or media file not found: {filepath_param}")

    elif static_path.is_file():

        # Return static file

        return static_file(static_path.name, root=str(static_path.parent))

    else:

        # Return 404 path not found

        abort(404, f"Path not found: /{path}")


def main():
    parser = argparse.ArgumentParser(
        prog="sigvie",
        description="Simple Image Gallery Viewer",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=30255,
        help="Port to listen on. Default: 30255.",
    )

    args = parser.parse_args()

    run(host="127.0.0.1", port=args.port, debug=False, reloader=False)


if __name__ == "__main__":
    main()