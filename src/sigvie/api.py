from pathlib import Path

from bottle import abort, request, static_file

from .util import Utils


class Api:
    def get_media(self):
        filepath_param = request.query.decode().get("filepath", "").strip()

        if not filepath_param:
            abort(400, "Missing filepath parameter.")

        media_path = Path(filepath_param).expanduser().resolve(strict=False)

        if not Utils.is_media_file(media_path):
            abort(404, f"File does not exist or is not a supported media file: {media_path}")

        file_response = static_file(media_path.name, root=str(media_path.parent))
        file_response.set_header("Cache-Control", "public, max-age=31536000")

        return file_response