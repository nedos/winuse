from __future__ import annotations

import pyautogui


def move(x: int, y: int, duration: float = 0.0) -> None:
    pyautogui.moveTo(x, y, duration=duration)


def click(x: int | None = None, y: int | None = None, button: str = "left", clicks: int = 1) -> None:
    if x is not None and y is not None:
        pyautogui.click(x=x, y=y, button=button, clicks=clicks)
    else:
        pyautogui.click(button=button, clicks=clicks)
