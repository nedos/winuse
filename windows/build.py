import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent
    spec_args = [
        "pyinstaller",
        "--noconfirm",
        "--noconsole",
        "--hidden-import",
        "win32clipboard",
        "--hidden-import",
        "win32con",
        "--name",
        "WinUse",
        str(root / "winuse" / "__main__.py"),
    ]
    return subprocess.call(spec_args)


if __name__ == "__main__":
    raise SystemExit(main())
