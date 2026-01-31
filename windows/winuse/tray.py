from __future__ import annotations

import os
import threading
import time
from typing import Optional

import pystray
from PIL import Image, ImageDraw, ImageFont
import uvicorn

from winuse.app import create_app
from winuse.config import load_settings


class ServerRunner:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self._server: Optional[uvicorn.Server] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self.is_running():
            return
        config = uvicorn.Config(
            create_app(),
            host=self.host,
            port=self.port,
            log_level="info",
            log_config=None,
            access_log=False,
        )
        self._server = uvicorn.Server(config)
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()
        time.sleep(0.25)

    def stop(self) -> None:
        if not self.is_running():
            return
        assert self._server is not None
        self._server.should_exit = True
        if self._thread:
            self._thread.join(timeout=2)
        self._server = None
        self._thread = None

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()


def _make_icon() -> Image.Image:
    img = Image.new("RGB", (64, 64), color=(24, 24, 24))
    draw = ImageDraw.Draw(img)
    fg = (235, 235, 235)
    accent = (255, 90, 90)

    # Laptop
    draw.rectangle((10, 26, 54, 48), outline=fg, width=2)
    draw.rectangle((12, 28, 52, 46), outline=fg, width=1)
    draw.rectangle((8, 48, 56, 54), outline=fg, width=2)

    # Person behind laptop (head + shoulders)
    draw.ellipse((22, 10, 32, 20), outline=fg, width=2)
    draw.arc((18, 16, 36, 34), start=200, end=340, fill=fg, width=2)

    # !!! indicator
    font = ImageFont.load_default()
    draw.text((36, 8), "!!!", fill=accent, font=font)
    return img


def run_tray() -> None:
    settings = load_settings()
    runner = ServerRunner(settings.api_host, settings.api_port)

    def _start(_icon, _item):
        runner.start()

    def _stop(_icon, _item):
        runner.stop()

    def _open_captures(_icon, _item):
        os.startfile(settings.output_dir)

    def _quit(icon, _item):
        runner.stop()
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("Start API", _start),
        pystray.MenuItem("Stop API", _stop),
        pystray.MenuItem("Open Captures", _open_captures),
        pystray.MenuItem("Quit", _quit),
    )

    icon = pystray.Icon("WinUse", _make_icon(), "WinUse", menu)
    runner.start()
    icon.run()
