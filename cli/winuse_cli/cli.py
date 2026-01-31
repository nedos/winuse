from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import requests

DEFAULT_HOST = "http://127.0.0.1:8080"


def _host_from_env() -> str:
    return os.getenv("WINUSE_HOST", DEFAULT_HOST)


def _print(data: Any) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")


def _request(method: str, host: str, path: str, json_body: Any | None = None) -> Any:
    url = host.rstrip("/") + path
    try:
        resp = requests.request(method, url, json=json_body, timeout=30)
    except requests.RequestException as exc:
        sys.stderr.write(f"Request failed: {exc}\n")
        raise SystemExit(2)

    if resp.status_code >= 400:
        sys.stderr.write(f"HTTP {resp.status_code}: {resp.text}\n")
        raise SystemExit(2)

    try:
        return resp.json()
    except Exception:
        return {"raw": resp.text}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="winuse", description="WinUse CLI")
    parser.add_argument(
        "--host",
        default=_host_from_env(),
        help="WinUse API host (default: $WINUSE_HOST or http://127.0.0.1:8080)",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("health", help="Check server health")
    sub.add_parser("windows", help="List windows")
    sub.add_parser("active", help="Get active window")

    p_focus = sub.add_parser("focus", help="Focus a window")
    p_focus.add_argument("hwnd", type=int)

    p_min = sub.add_parser("minimize", help="Minimize a window")
    p_min.add_argument("hwnd", type=int)

    p_max = sub.add_parser("maximize", help="Maximize a window")
    p_max.add_argument("hwnd", type=int)

    p_restore = sub.add_parser("restore", help="Restore a window")
    p_restore.add_argument("hwnd", type=int)

    p_shot = sub.add_parser("screenshot", help="Take a screenshot")
    p_shot.add_argument("--hwnd", type=int, default=None)

    p_move = sub.add_parser("mouse-move", help="Move the mouse")
    p_move.add_argument("x", type=int)
    p_move.add_argument("y", type=int)
    p_move.add_argument("--duration", type=float, default=0.0)

    p_click = sub.add_parser("mouse-click", help="Click the mouse")
    p_click.add_argument("--x", type=int, default=None)
    p_click.add_argument("--y", type=int, default=None)
    p_click.add_argument("--button", choices=["left", "right", "middle"], default="left")
    p_click.add_argument("--clicks", type=int, default=1)

    p_type = sub.add_parser("type", help="Type or paste text")
    p_type.add_argument("text")
    p_type.add_argument("--interval", type=float, default=0.0)
    p_type.add_argument("--mode", choices=["paste", "type"], default="paste")

    p_paste = sub.add_parser("paste", help="Paste text via clipboard")
    p_paste.add_argument("text")

    p_press = sub.add_parser("press", help="Press key(s)")
    p_press.add_argument("keys", nargs="+")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    host = args.host
    if args.cmd == "health":
        _print(_request("GET", host, "/health"))
        return

    if args.cmd == "windows":
        _print(_request("GET", host, "/windows"))
        return

    if args.cmd == "active":
        _print(_request("GET", host, "/windows/active"))
        return

    if args.cmd == "focus":
        _print(_request("POST", host, f"/windows/{args.hwnd}/focus"))
        return

    if args.cmd == "minimize":
        _print(_request("POST", host, f"/windows/{args.hwnd}/minimize"))
        return

    if args.cmd == "maximize":
        _print(_request("POST", host, f"/windows/{args.hwnd}/maximize"))
        return

    if args.cmd == "restore":
        _print(_request("POST", host, f"/windows/{args.hwnd}/restore"))
        return

    if args.cmd == "screenshot":
        payload = {}
        if args.hwnd is not None:
            payload["hwnd"] = args.hwnd
        _print(_request("POST", host, "/screenshot", payload))
        return

    if args.cmd == "mouse-move":
        payload = {"x": args.x, "y": args.y, "duration": args.duration}
        _print(_request("POST", host, "/mouse/move", payload))
        return

    if args.cmd == "mouse-click":
        payload = {
            "x": args.x,
            "y": args.y,
            "button": args.button,
            "clicks": args.clicks,
        }
        _print(_request("POST", host, "/mouse/click", payload))
        return

    if args.cmd == "type":
        payload = {"text": args.text, "interval": args.interval, "mode": args.mode}
        _print(_request("POST", host, "/keyboard/type", payload))
        return

    if args.cmd == "paste":
        payload = {"text": args.text}
        _print(_request("POST", host, "/keyboard/paste", payload))
        return

    if args.cmd == "press":
        payload = {"keys": args.keys}
        _print(_request("POST", host, "/keyboard/press", payload))
        return

    parser.error("Unknown command")


if __name__ == "__main__":
    main()
