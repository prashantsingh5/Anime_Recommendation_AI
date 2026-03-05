from __future__ import annotations

import argparse

try:
    from .api import create_app
    from .user_interface import start_conversation
except ImportError:
    from api import create_app
    from user_interface import start_conversation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Anime Recommendation AI")
    parser.add_argument(
        "--mode",
        choices=["chat", "api"],
        default="chat",
        help="Run as interactive chat or Flask API.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="API host when mode=api")
    parser.add_argument("--port", type=int, default=5000, help="API port when mode=api")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "chat":
        start_conversation()
        return

    app = create_app()
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
