from bottle import Bottle, TEMPLATE_PATH, abort, run, static_file

from .api import Api
from .constant import BASE_DIR
from .view import View


class App:
    def __init__(
            self,
            host: str = "127.0.0.1",
            port: int = 30255,
            debug: bool = False,
            reloader: bool = False,
    ):
        self.host = host
        self.port = port
        self.debug = debug
        self.reloader = reloader

        self.bottle = Bottle()
        self.api = Api()
        self.view = View()

        TEMPLATE_PATH.insert(0, str(BASE_DIR))

        self.register_endpoints()

    def register_endpoints(self):
        self.bottle.get("/")(self.view.get_index)
        self.bottle.post("/")(self.view.post_index)

        self.bottle.get("/media")(self.view.get_media)
        self.bottle.post("/media")(self.view.post_media)

        self.bottle.get("/api/media")(self.api.get_media)

        self.bottle.get("/<path:path>")(self.get_static)

    def get_static(self, path: str):
        static_path = BASE_DIR / path

        if static_path.is_file():
            return static_file(static_path.name, root=str(static_path.parent))

        abort(404, f"Path not found: /{path}")

    def run(self):
        run(
            app=self.bottle,
            host=self.host,
            port=self.port,
            debug=self.debug,
            reloader=self.reloader,
        )