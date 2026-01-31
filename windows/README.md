# WinUse (Windows app)

WinUse is a minimal Windows 11 automation API packaged as a tray app. It exposes a small REST interface for screenshots, window focus, and keyboard/mouse input so agents can reliably drive a Windows desktop over LAN.

This folder contains the Windows tray app + API server. Run all commands from this `windows/` directory.

Project homepage: `github.com/nedos/winuse`

## Features (v1)

- Enumerate windows (title, process, HWND, rect)
- Focus/minimize/maximize/restore by HWND
- Full-screen and per-window screenshots (saved to disk and served via `/files/...`)
- Mouse move and click
- Keyboard input with clipboard-first paste to preserve UTF-8

No UI Automation in v1 — only window handles and input simulation.

## Run (Windows)

1) Install Python 3.11+ on Windows
2) Copy this repo to the Windows machine
3) Install dependencies and start:

```powershell
pip install -r requirements.txt
python -m winuse
```

Default bind: `0.0.0.0:8080` (LAN accessible)

### Tray mode (default)

```powershell
python -m winuse
```

Starts the API in the background and adds a tray icon with Start/Stop/Open Captures/Quit.

### Server-only mode

```powershell
python -m winuse --server
```

## Build EXE (Windows)

```powershell
pip install -r requirements-dev.txt
python build.py
```

The executable will be in `dist/WinUse.exe`.

## Configuration

First run creates `config.yaml`:

```yaml
api:
  host: "0.0.0.0"
  port: 8080
  api_key: null
screenshots:
  output_dir: "C:\\winuse\\captures"
  format: "png"
```

Environment overrides:

- `WINUSE_API_HOST`
- `WINUSE_API_PORT`
- `WINUSE_API_KEY`
- `WINUSE_OUTPUT_DIR`
- `WINUSE_IMAGE_FORMAT`

## API reference

All responses:

```json
{ "success": true, "data": { ... }, "error": null }
```

### Health
- `GET /health`

### Windows
- `GET /windows`
- `GET /windows/active`
- `POST /windows/{hwnd}/focus`
- `POST /windows/{hwnd}/minimize`
- `POST /windows/{hwnd}/maximize`
- `POST /windows/{hwnd}/restore`

### Screenshot
- `POST /screenshot` (optional body: `{ "hwnd": 12345 }`)
- Files served at `GET /files/<filename>`

### Mouse
- `POST /mouse/move` body: `{ "x": 100, "y": 200, "duration": 0.0 }`
- `POST /mouse/click` body: `{ "x": 100, "y": 200, "button": "left", "clicks": 1 }`

### Keyboard
- `POST /keyboard/type` (default `mode=paste`)
- `POST /keyboard/paste` (clipboard-only, no fallback)
- `POST /keyboard/press`

Clipboard-first input uses the Windows clipboard to preserve UTF-8. If the clipboard API is unavailable, `/keyboard/type` falls back to simulated typing and returns a warning.

## Examples

```bash
# list windows
curl http://HOST:8080/windows | jq

# focus a window
curl -X POST http://HOST:8080/windows/12345/focus

# screenshot (returns path + url)
curl -X POST http://HOST:8080/screenshot | jq

# click
curl -X POST http://HOST:8080/mouse/click \
  -H "Content-Type: application/json" \
  -d '{"x": 500, "y": 300, "button": "left"}'

# type (paste by default)
curl -X POST http://HOST:8080/keyboard/type \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello"}'

# force clipboard paste (no fallback)
curl -X POST http://HOST:8080/keyboard/paste \
  -H "Content-Type: application/json" \
  -d '{"text": "Привет, Сам"}'
```

## Dev loop (WSL -> Windows)

1) Deploy to Windows:

```bash
./scripts/deploy.sh nedos@192.168.1.100 'C:/winuse'
```

2) Start server on Windows (over SSH):

```bash
ssh nedos@192.168.1.100 "powershell -NoProfile -File C:/winuse/scripts/run_server.ps1"
```

3) Run tests from WSL against Windows:

```bash
./scripts/test_remote.sh 192.168.1.100 8080
```

## Project layout

```
windows/
├── winuse/
│   ├── __main__.py
│   ├── app.py
│   ├── config.py
│   ├── tray.py
│   └── core/
│       ├── windows.py
│       ├── screenshot.py
│       ├── mouse.py
│       └── keyboard.py
├── tests/
│   └── test_api.py
├── scripts/
│   ├── deploy.sh
│   ├── run_server.ps1
│   └── test_remote.sh
├── requirements.txt
├── requirements-dev.txt
├── build.py
├── config.yaml
└── README.md
```

## License

MIT. See `../LICENSE`.
