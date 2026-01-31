import os
from dataclasses import dataclass
from typing import Any, Dict

import yaml


DEFAULT_CONFIG = {
    "api": {
        "host": "0.0.0.0",
        "port": 8080,
        "api_key": None,
    },
    "screenshots": {
        "output_dir": r"C:\\winuse\\captures",
        "format": "png",
    },
    "behavior": {
        "failsafe": True,
    },
}


@dataclass
class Settings:
    api_host: str
    api_port: int
    api_key: str | None
    output_dir: str
    image_format: str
    failsafe: bool


def _merge_defaults(cfg: Dict[str, Any]) -> Dict[str, Any]:
    merged = {
        "api": dict(DEFAULT_CONFIG["api"]),
        "screenshots": dict(DEFAULT_CONFIG["screenshots"]),
        "behavior": dict(DEFAULT_CONFIG["behavior"]),
    }
    for section in ("api", "screenshots", "behavior"):
        merged[section].update(cfg.get(section, {}))
    return merged


def _apply_env_overrides(cfg: Dict[str, Any]) -> Dict[str, Any]:
    host = os.getenv("WINUSE_API_HOST")
    port = os.getenv("WINUSE_API_PORT")
    api_key = os.getenv("WINUSE_API_KEY")
    out_dir = os.getenv("WINUSE_OUTPUT_DIR")
    fmt = os.getenv("WINUSE_IMAGE_FORMAT")
    failsafe = os.getenv("WINUSE_FAILSAFE")

    if host:
        cfg["api"]["host"] = host
    if port:
        try:
            cfg["api"]["port"] = int(port)
        except ValueError:
            pass
    if api_key is not None:
        cfg["api"]["api_key"] = api_key
    if out_dir:
        cfg["screenshots"]["output_dir"] = out_dir
    if fmt:
        cfg["screenshots"]["format"] = fmt
    if failsafe is not None:
        cfg["behavior"]["failsafe"] = str(failsafe).lower() in ("1", "true", "yes", "on")
    return cfg


def load_settings(config_path: str = "config.yaml") -> Settings:
    cfg: Dict[str, Any] = {}
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    cfg = _merge_defaults(cfg)
    cfg = _apply_env_overrides(cfg)

    # Persist a default config on first run for visibility.
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f, sort_keys=False)

    output_dir = cfg["screenshots"]["output_dir"]
    os.makedirs(output_dir, exist_ok=True)

    return Settings(
        api_host=str(cfg["api"]["host"]),
        api_port=int(cfg["api"]["port"]),
        api_key=cfg["api"].get("api_key") or None,
        output_dir=output_dir,
        image_format=str(cfg["screenshots"].get("format", "png")),
        failsafe=bool(cfg["behavior"].get("failsafe", True)),
    )
