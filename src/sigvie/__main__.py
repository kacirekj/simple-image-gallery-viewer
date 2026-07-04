import argparse
from base64 import urlsafe_b64decode, urlsafe_b64encode
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

INDEX_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Sigvie - Simple Image Gallery Viewer</title>
    <style>
        body {
            margin: 0;
            padding: 16px;
            font-family: system-ui, sans-serif;
        }

        form {
        }

        input[type="text"] {
            box-sizing: border-box;
            width: 100%;
            padding: 8px;
        }

        main {
        }

        .help {
            max-width: 35em;
        }

        section {
            margin-bottom: 64px;
        }

        img,
        video {
            width: 290px;
            margin-right: 16px;
            margin-bottom: 16px;
            display: inline;
            vertical-align: top;
        }

        video {
            background: #222;
        }

        .empty {
            color: #666;
        }
    </style>
</head>
<body>
    <header>
        <form action="/" method="get">
            <input
                id="directoryid"
                type="text"
                name="directory"
                value="{{directory_path}}"
                placeholder="/home/jiri/Pictures"
            >
        </form>
    </header>

    <main>
        % if directory:
            % if media_infos_groups:
                % for year_month, media_infos in media_infos_groups.items():
                    <h1>{{Utils.year_month_label(year_month)}}</h1>

                    <section>
                        % for media in media_infos:
                            % if media.media_type == MediaType.IMAGE:
                                <a href="{{media.media_url}}">
                                    <img
                                        src="{{media.media_url}}"
                                        loading="lazy"
                                        alt=""
                                        title="{{media.path}}&#10;media time: {{media.media_time}}&#10;created: {{media.created_time}}&#10;modified: {{media.modified_time}}"
                                    >
                                </a>
                            % elif media.media_type == MediaType.VIDEO:
                                <video
                                    src="{{media.media_url}}"
                                    controls
                                    preload="metadata"
                                    title="{{media.path}}&#10;media time: {{media.media_time}}&#10;created: {{media.created_time}}&#10;modified: {{media.modified_time}}"
                                ></video>
                            % end
                        % end
                    </section>
                % end
            % else:
                <p class="empty">There aren't any media files in this directory.</p>
            % end
        % else:
            <div class="help">
                <h1>Sigvie - Simple Image Gallery Viewer</h1>
                <ul>
                    <li>
                        Enter the path to a directory containing the images and videos you want to display                    </li>
                    <li>
                        Use <code>Ctrl+</code> and <code>Ctrl-</code> to change how many items are visible on the page
                    </li>
                    <li>
                        Use <code>Pinch-to-zoom</code> on your touchpad to zoom individual images.
                    </li>
                    <li>
                        Use Back and Forward to navigate into image details 
                    </li>
                    <li>
                        If the directory contains too many media files, the page may become slow or laggy.
                        For better performance, organize your media into smaller folders.
                    </li>
                </ul>
            </div>
        % end
    </main>
</body>
</html>
"""


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
    def encode_path(path: Path) -> str:
        return urlsafe_b64encode(str(path).encode("utf-8")).decode("ascii")

    @staticmethod
    def decode_path(encoded_path: str) -> Path:
        decoded = urlsafe_b64decode(encoded_path.encode("ascii")).decode("utf-8")
        return Path(decoded)

    @staticmethod
    def create_media_url(path: Path) -> str:
        return "/api/media?id=" + Utils.encode_path(path)

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
            media_url=Utils.create_media_url(path),
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
    encoded_path = request.query.get("id")

    if not encoded_path:
        abort(400, "Missing id parameter.")

    try:
        media_path = Utils.decode_path(encoded_path)
    except Exception:
        abort(400, "The id parameter is not a valid base64 path.")

    if not Utils.is_media_file(media_path):
        abort(404, f"File does not exist or is not a supported media file: {media_path}")

    file_response = static_file(media_path.name, root=str(media_path.parent))
    file_response.set_header("Cache-Control", "public, max-age=31536000")

    return file_response


@route("/")
def index():
    directory_path = request.query.get("directory", "").strip()

    directory = None
    media_infos_groups = None

    if directory_path:
        directory = Path(directory_path).expanduser()

        if not directory.is_dir():
            abort(404, f"Directory not found: {directory}")

        media_infos = Utils.create_media_infos(directory)
        media_infos_groups = Utils.create_groups(media_infos)

    return template(
        INDEX_TEMPLATE,
        directory=directory,
        directory_path=directory_path,
        media_infos_groups=media_infos_groups,
        MediaType=MediaType,
        Utils=Utils,
    )


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
