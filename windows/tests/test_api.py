import os
import time

import httpx
import pytest

HOST = os.getenv("WINUSE_HOST", "http://127.0.0.1:8080")


@pytest.fixture(scope="session")
def client():
    return httpx.Client(base_url=HOST, timeout=10)


def wait_for_server(client: httpx.Client, timeout_s: float = 10.0) -> None:
    start = time.time()
    while time.time() - start < timeout_s:
        try:
            r = client.get("/health")
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.5)
    pytest.fail("WinUse server not responding at /health")


def test_health(client):
    wait_for_server(client)
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"


def test_windows_list(client):
    r = client.get("/windows")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_windows_active(client):
    r = client.get("/windows/active")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True


def test_mouse_move(client):
    r = client.post("/mouse/move", json={"x": 10, "y": 10, "duration": 0})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True


def test_mouse_click(client):
    r = client.post("/mouse/click", json={"x": 10, "y": 10, "button": "left", "clicks": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True


def test_keyboard_type(client):
    r = client.post("/keyboard/type", json={"text": "winuse test", "interval": 0})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True


def test_keyboard_press(client):
    r = client.post("/keyboard/press", json={"keys": ["shift", "tab"]})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True


def test_screenshot_full(client):
    r = client.post("/screenshot", json={})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert "url" in body["data"]
    # Fetch the file
    file_url = body["data"]["url"]
    fr = client.get(file_url)
    assert fr.status_code == 200
