#!/usr/bin/env python3
import json
import os
import time
from datetime import datetime
from urllib import request
from urllib.error import URLError, HTTPError


def load_env(path: str) -> None:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def _req(method: str, host: str, path: str, body: dict | None = None) -> dict:
    url = host.rstrip("/") + path
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                return json.loads(raw)
            except Exception:
                return {"raw": raw}
    except HTTPError as exc:
        raise SystemExit(f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}")
    except URLError as exc:
        raise SystemExit(f"Request failed: {exc}")


def main() -> None:
    load_env(os.path.join(os.path.dirname(__file__), "..", ".env"))

    host = os.environ.get("WINUSE_HOST", "http://127.0.0.1:8080")
    os.environ.setdefault("NO_PROXY", "*")
    os.environ.setdefault("no_proxy", "*")

    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    msg = f"integration-test-{ts}"

    _req("POST", host, "/keyboard/press", {"keys": ["winleft", "r"]})
    time.sleep(1)
    _req("POST", host, "/keyboard/type", {"text": "cmd", "mode": "paste"})
    time.sleep(0.5)
    _req("POST", host, "/keyboard/press", {"keys": ["enter"]})
    time.sleep(1)
    _req("POST", host, "/keyboard/type", {"text": msg, "mode": "paste"})
    _req("POST", host, "/keyboard/press", {"keys": ["enter"]})
    time.sleep(0.5)

    shot = _req("POST", host, "/screenshot", {})
    print(json.dumps({"sent": msg, "screenshot": shot}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
