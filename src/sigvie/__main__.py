import argparse

from .app import App


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

    app = App(
        host="127.0.0.1",
        port=args.port,
        debug=False,
        reloader=False,
    )
    app.run()


if __name__ == "__main__":
    main()