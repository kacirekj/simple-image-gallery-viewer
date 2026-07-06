from pathlib import Path

from bottle import abort, request, template

from .model import MediaType
from .util import Utils


class View:
    def get_index(self):
        filepath_param = request.query.decode().get("filepath", "").strip()

        return template(
            "templates/page/index_page.html",
            filepath=filepath_param,
            Utils=Utils,
        )

    def post_index(self):
        return ""

    def get_media(self):
        filepath_param = request.query.decode().get("filepath", "").strip()

        if filepath_param:
            filepath = Path(filepath_param).expanduser().resolve(strict=False)
        else:
            filepath = None

        if filepath and filepath.is_dir():

            # Return media_gallery_page.html

            directory = filepath
            media_infos = Utils.create_media_infos(directory)
            media_infos_groups = Utils.create_groups(media_infos)

            return template(
                "templates/page/media_gallery_page.html",
                filepath=filepath_param,
                media_infos_groups=media_infos_groups,
                MediaType=MediaType,
                Utils=Utils,
            )

        elif filepath and filepath.is_file():

            # Return media_single_page.html

            media_info = Utils.create_media_info(filepath)

            return template(
                "templates/page/media_single_page.html",
                filepath=filepath_param,
                media=media_info,
                MediaType=MediaType,
                Utils=Utils,
            )

        elif filepath_param:

            # Return 404 filepath not found

            abort(404, f"Directory or media file not found: {filepath_param}")

        else:

            # Return 400 missing filepath

            abort(400, "Missing filepath parameter.")

    def post_media(self):
        return ""