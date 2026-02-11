import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WINUSE_URL = os.getenv("WINUSE_URL", "http://localhost:8080")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "5000"))
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "")  # comma-separated telegram user IDs

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN required")
if not WEBHOOK_URL:
    raise ValueError("WEBHOOK_URL required")


def normalize_winuse_url(url: str) -> str:
    """Normalize to http(s)://host:port."""
    url = url.strip().rstrip("/")
    if url.startswith(("http://", "https://")):
        return url
    if ":" in url:
        host, port = url.rsplit(":", 1)
        if port.isdigit():
            return f"http://{url}"
    return f"http://{url}:8080"


WINUSE_BASE = normalize_winuse_url(WINUSE_URL)


def check_user(user_id: int) -> bool:
    """Check if user is allowed. Empty ALLOWED_USERS = allow all."""
    if not ALLOWED_USERS:
        return True
    allowed = [uid.strip() for uid in ALLOWED_USERS.split(",")]
    return str(user_id) in allowed
