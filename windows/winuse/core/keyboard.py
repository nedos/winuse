from __future__ import annotations

import pyautogui

try:
    import win32clipboard
    import win32con
except Exception:  # pragma: no cover - optional Windows-only dependency
    win32clipboard = None
    win32con = None


def type_text(text: str, interval: float = 0.0) -> None:
    pyautogui.write(text, interval=interval)


def paste_text(text: str, *, allow_fallback: bool = True) -> bool:
    if win32clipboard and win32con:
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        finally:
            win32clipboard.CloseClipboard()
        pyautogui.hotkey("ctrl", "v")
        return True

    if allow_fallback:
        pyautogui.write(text)
        return False

    raise RuntimeError("Clipboard unavailable (win32clipboard not loaded)")


def press_keys(keys: list[str]) -> None:
    if len(keys) == 1:
        pyautogui.press(keys[0])
    else:
        pyautogui.hotkey(*keys)
