from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import pyautogui

from winuse.config import Settings, load_settings
from winuse.core import keyboard as kb
from winuse.core import mouse, screenshot, windows


class MouseMoveRequest(BaseModel):
    x: int
    y: int
    duration: float = 0.0


class MouseClickRequest(BaseModel):
    x: Optional[int] = None
    y: Optional[int] = None
    button: str = Field(default="left", pattern="^(left|right|middle)$")
    clicks: int = 1


class KeyboardTypeRequest(BaseModel):
    text: str
    interval: float = 0.0
    mode: str = Field(default="paste", pattern="^(paste|type)$")


class KeyboardPressRequest(BaseModel):
    keys: list[str]


class ScreenshotRequest(BaseModel):
    hwnd: Optional[int] = None


def _ok(data: Any) -> Dict[str, Any]:
    return {"success": True, "data": data, "error": None}


def _err(code: str, message: str) -> Dict[str, Any]:
    return {"success": False, "data": None, "error": {"code": code, "message": message}}


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    app = FastAPI(title="WinUse")
    pyautogui.FAILSAFE = settings.failsafe

    app.mount("/files", StaticFiles(directory=settings.output_dir), name="files")

    @app.get("/health")
    def health():
        return _ok({"status": "ok"})

    @app.get("/windows")
    def list_windows():
        try:
            return _ok(windows.list_windows())
        except Exception as exc:
            return _err("WINDOW_LIST_FAILED", str(exc))

    @app.get("/windows/active")
    def active_window():
        try:
            return _ok(windows.get_active_window())
        except Exception as exc:
            return _err("WINDOW_ACTIVE_FAILED", str(exc))

    @app.post("/windows/{hwnd}/focus")
    def focus_window(hwnd: int):
        try:
            windows.focus_window(hwnd)
            return _ok({"hwnd": hwnd})
        except Exception as exc:
            return _err("WINDOW_FOCUS_FAILED", str(exc))

    @app.post("/windows/{hwnd}/minimize")
    def minimize_window(hwnd: int):
        try:
            windows.minimize_window(hwnd)
            return _ok({"hwnd": hwnd})
        except Exception as exc:
            return _err("WINDOW_MINIMIZE_FAILED", str(exc))

    @app.post("/windows/{hwnd}/maximize")
    def maximize_window(hwnd: int):
        try:
            windows.maximize_window(hwnd)
            return _ok({"hwnd": hwnd})
        except Exception as exc:
            return _err("WINDOW_MAXIMIZE_FAILED", str(exc))

    @app.post("/windows/{hwnd}/restore")
    def restore_window(hwnd: int):
        try:
            windows.restore_window(hwnd)
            return _ok({"hwnd": hwnd})
        except Exception as exc:
            return _err("WINDOW_RESTORE_FAILED", str(exc))

    @app.post("/screenshot")
    def take_screenshot(req: ScreenshotRequest | None = None):
        try:
            if req and req.hwnd is not None:
                result = screenshot.capture_window(settings.output_dir, req.hwnd, settings.image_format)
            else:
                result = screenshot.capture_full(settings.output_dir, settings.image_format)
            url = f"/files/{result['filename']}"
            return _ok({"path": result["path"], "url": url})
        except Exception as exc:
            return _err("SCREENSHOT_FAILED", str(exc))

    @app.post("/mouse/move")
    def mouse_move(req: MouseMoveRequest):
        try:
            mouse.move(req.x, req.y, duration=req.duration)
            return _ok({"x": req.x, "y": req.y})
        except Exception as exc:
            return _err("MOUSE_MOVE_FAILED", str(exc))

    @app.post("/mouse/click")
    def mouse_click(req: MouseClickRequest):
        try:
            mouse.click(req.x, req.y, button=req.button, clicks=req.clicks)
            return _ok({"x": req.x, "y": req.y, "button": req.button, "clicks": req.clicks})
        except Exception as exc:
            return _err("MOUSE_CLICK_FAILED", str(exc))

    @app.post("/keyboard/type")
    def keyboard_type(req: KeyboardTypeRequest):
        try:
            if req.mode == "paste":
                pasted = kb.paste_text(req.text, allow_fallback=True)
                mode = "paste" if pasted else "type"
                payload = {"text": req.text, "mode": mode}
                if not pasted:
                    payload["warning"] = "clipboard_unavailable_fallback"
                return _ok(payload)
            kb.type_text(req.text, interval=req.interval)
            return _ok({"text": req.text, "mode": "type"})
        except Exception as exc:
            return _err("KEYBOARD_TYPE_FAILED", str(exc))

    @app.post("/keyboard/paste")
    def keyboard_paste(req: KeyboardTypeRequest):
        try:
            kb.paste_text(req.text, allow_fallback=False)
            return _ok({"text": req.text, "mode": "paste"})
        except Exception as exc:
            return _err("KEYBOARD_PASTE_FAILED", str(exc))

    @app.post("/keyboard/press")
    def keyboard_press(req: KeyboardPressRequest):
        try:
            kb.press_keys(req.keys)
            return _ok({"keys": req.keys})
        except Exception as exc:
            return _err("KEYBOARD_PRESS_FAILED", str(exc))

    return app


app = create_app()
