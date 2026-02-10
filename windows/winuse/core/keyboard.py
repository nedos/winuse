from __future__ import annotations

import pyautogui

try:
    import win32clipboard
    import win32con
    import win32gui
except Exception:  # pragma: no cover - optional Windows-only dependency
    win32clipboard = None
    win32con = None
    win32gui = None


def type_text(text: str, interval: float = 0.0) -> None:
    pyautogui.write(text, interval=interval)


WM_PASTE = 0x0302


def paste_text(text: str, *, keys: list[str] | None = None, allow_fallback: bool = True) -> bool:
    if win32clipboard and win32con:
        win32clipboard.OpenClipboard()
        try:
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        finally:
            win32clipboard.CloseClipboard()

        # Try WM_PASTE first (works for Windows Terminal, edit controls, etc.)
        if not keys:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                win32gui.SendMessage(hwnd, WM_PASTE, 0, 0)
                return True

        # Fall back to keyboard shortcut (custom paste_keys or ctrl+v)
        paste_keys = keys or ["ctrl", "v"]
        pyautogui.hotkey(*paste_keys)
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
