from __future__ import annotations

from typing import Dict, List

import win32api
import win32con
import win32gui
import win32process

try:
    import psutil
except Exception:  # pragma: no cover - optional dependency at runtime
    psutil = None


def _get_process_name(pid: int) -> str | None:
    if not psutil:
        return None
    try:
        return psutil.Process(pid).name()
    except Exception:
        return None


def get_window_rect(hwnd: int) -> Dict[str, int]:
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    return {
        "x": int(left),
        "y": int(top),
        "width": int(right - left),
        "height": int(bottom - top),
    }


def list_windows() -> List[Dict[str, object]]:
    windows: List[Dict[str, object]] = []

    def enum_handler(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        windows.append(
            {
                "hwnd": int(hwnd),
                "title": title,
                "pid": int(pid),
                "process": _get_process_name(pid),
                "rect": get_window_rect(hwnd),
            }
        )

    win32gui.EnumWindows(enum_handler, None)
    return windows


def get_active_window() -> Dict[str, object] | None:
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None
    title = win32gui.GetWindowText(hwnd)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    return {
        "hwnd": int(hwnd),
        "title": title,
        "pid": int(pid),
        "process": _get_process_name(pid),
        "rect": get_window_rect(hwnd),
    }


def _last_error_message() -> str:
    code = win32api.GetLastError()
    if not code:
        return "no_error"
    message = win32api.FormatMessage(code).strip()
    return f"{code}: {message}"


def focus_window(hwnd: int) -> None:
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.BringWindowToTop(hwnd)

    def is_foreground() -> bool:
        return win32gui.GetForegroundWindow() == hwnd

    def set_foreground() -> bool:
        try:
            win32gui.SetForegroundWindow(hwnd)
        except win32gui.error:
            return False
        return is_foreground()

    if set_foreground():
        return

    current_tid = win32api.GetCurrentThreadId()
    fg_hwnd = win32gui.GetForegroundWindow()
    fg_tid, _ = win32process.GetWindowThreadProcessId(fg_hwnd)
    target_tid, _ = win32process.GetWindowThreadProcessId(hwnd)
    attached_fg = False
    attached_target = False
    try:
        attached_fg = win32process.AttachThreadInput(current_tid, fg_tid, True)
        attached_target = win32process.AttachThreadInput(current_tid, target_tid, True)
        win32gui.SetForegroundWindow(hwnd)
        win32gui.SetActiveWindow(hwnd)
        win32gui.SetFocus(hwnd)
    finally:
        if attached_target:
            win32process.AttachThreadInput(current_tid, target_tid, False)
        if attached_fg:
            win32process.AttachThreadInput(current_tid, fg_tid, False)

    if is_foreground():
        return

    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    if set_foreground():
        return

    raise RuntimeError(f"SetForegroundWindow failed ({_last_error_message()})")


def minimize_window(hwnd: int) -> None:
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)


def maximize_window(hwnd: int) -> None:
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


def restore_window(hwnd: int) -> None:
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
