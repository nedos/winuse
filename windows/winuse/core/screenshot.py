from __future__ import annotations

import os
from datetime import datetime
from typing import Dict, Optional

import mss
from PIL import Image

from winuse.core.windows import get_window_rect


def _timestamp_name(ext: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    return f"capture_{ts}.{ext}"


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _save_mss_image(grab, output_path: str) -> None:
    img = Image.frombytes("RGB", grab.size, grab.rgb)
    img.save(output_path)


def capture_full(output_dir: str, fmt: str = "png") -> Dict[str, str]:
    _ensure_dir(output_dir)
    filename = _timestamp_name(fmt)
    output_path = os.path.join(output_dir, filename)
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        grab = sct.grab(monitor)
        _save_mss_image(grab, output_path)
    return {"path": output_path, "filename": filename}


def capture_window(output_dir: str, hwnd: int, fmt: str = "png") -> Dict[str, str]:
    _ensure_dir(output_dir)
    rect = get_window_rect(hwnd)
    filename = _timestamp_name(fmt)
    output_path = os.path.join(output_dir, filename)
    with mss.mss() as sct:
        monitor = {
            "left": rect["x"],
            "top": rect["y"],
            "width": rect["width"],
            "height": rect["height"],
        }
        grab = sct.grab(monitor)
        _save_mss_image(grab, output_path)
    return {"path": output_path, "filename": filename}
