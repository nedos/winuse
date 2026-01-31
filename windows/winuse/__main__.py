import argparse

import uvicorn

from winuse.app import create_app
from winuse.config import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="WinUse API server")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--tray", action="store_true", help="Run system tray app (default)")
    parser.add_argument("--server", action="store_true", help="Run API server only")
    args = parser.parse_args()

    if args.tray or not args.server:
        from winuse.tray import run_tray

        run_tray()
        return

    settings = load_settings(args.config)
    host = args.host or settings.api_host
    port = args.port or settings.api_port

    app = create_app(settings)
    uvicorn.run(app, host=host, port=port, log_level="info", log_config=None, access_log=False)


if __name__ == "__main__":
    main()
