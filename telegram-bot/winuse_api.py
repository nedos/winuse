"""Async WinUse API client."""

from __future__ import annotations

import httpx
from config import WINUSE_BASE


async def api_get(path: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{WINUSE_BASE}{path}")
        resp.raise_for_status()
        return resp.json()


async def api_post(path: str, data: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{WINUSE_BASE}{path}", json=data)
        resp.raise_for_status()
        return resp.json()


async def api_get_bytes(path: str) -> bytes:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(f"{WINUSE_BASE}{path}")
        resp.raise_for_status()
        return resp.content


async def list_windows() -> list[dict]:
    result = await api_get("/windows")
    return result.get("data", [])


async def get_active_window() -> dict | None:
    result = await api_get("/windows/active")
    return result.get("data") if result.get("success") else None


async def focus_window(hwnd: int) -> bool:
    result = await api_post(f"/windows/{hwnd}/focus")
    return result.get("success", False)


async def find_window_by_title(title: str) -> dict | None:
    """Find first window whose title contains the given string (case-insensitive)."""
    windows = await list_windows()
    title_lower = title.lower()
    for w in windows:
        if title_lower in w.get("title", "").lower():
            return w
    return None


async def press_keys(keys: list[str]) -> bool:
    result = await api_post("/keyboard/press", {"keys": keys})
    return result.get("success", False)


async def type_text(text: str, mode: str = "type") -> bool:
    result = await api_post("/keyboard/type", {"text": text, "mode": mode})
    return result.get("success", False)


async def paste_text(text: str | None = None) -> bool:
    data = {"text": text} if text else {}
    result = await api_post("/keyboard/paste", data)
    return result.get("success", False)


async def take_screenshot(hwnd: int | None = None) -> bytes | None:
    """Take screenshot and return PNG bytes. If hwnd given, screenshot that window."""
    data = {"hwnd": hwnd} if hwnd else {}
    result = await api_post("/screenshot", data)
    if not result.get("success"):
        return None
    file_url = result.get("data", {}).get("url", "")
    if not file_url:
        return None
    return await api_get_bytes(file_url)


async def mouse_click(x: int, y: int, double: bool = False) -> bool:
    data: dict = {"x": x, "y": y}
    if double:
        data["double"] = True
    result = await api_post("/mouse/click", data)
    return result.get("success", False)


async def mouse_move(x: int, y: int) -> bool:
    result = await api_post("/mouse/move", {"x": x, "y": y})
    return result.get("success", False)


async def minimize_window(hwnd: int) -> bool:
    result = await api_post(f"/windows/{hwnd}/minimize")
    return result.get("success", False)


async def maximize_window(hwnd: int) -> bool:
    result = await api_post(f"/windows/{hwnd}/maximize")
    return result.get("success", False)


async def restore_window(hwnd: int) -> bool:
    result = await api_post(f"/windows/{hwnd}/restore")
    return result.get("success", False)
