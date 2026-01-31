# WinUse

**Computer-use for Windows. No $700 Mac Mini rack required.**

WinUse makes Windows usable for AI agents. It's a tray app + FastAPI server that exposes screenshots, mouse, keyboard, and window management as a dead-simple REST API. Point any agent at it and go.

While everyone else is buying Mac Minis to run `openclaw` in computer use mode, you can just... run this on any Windows box you already own. That $200 Dell OptiPlex in the closet? Yeah, that works.

## What it does

- 📸 Full-screen or per-window screenshots
- 🖱️ Mouse move, click (left/right/middle, single/double)
- ⌨️ Keyboard input with clipboard-first paste for UTF-8 safety
- 🪟 Window management — list, focus, minimize, maximize, restore by HWND

No UI Automation, no accessibility tree, no COM nonsense. Just window handles and input simulation. The xdotool approach, but for Windows, over HTTP.

## Repository layout

```
winuse/
├── windows/   — Windows tray app + API server (runs on the Windows machine)
├── cli/       — winuse CLI (runs anywhere that can reach the API)
└── scripts/   — helpers for WSL → Windows integration testing
```

## Quick start

### Windows host

See [`windows/README.md`](windows/README.md) for build/run instructions. TL;DR: run the app, it sits in your system tray, serves the API on port 8080.

### CLI

```bash
pip install winuse-cli
export WINUSE_HOST="http://<windows-ip>:8080"

winuse health
winuse screenshot
winuse paste "Hello from the future 🤖"
winuse press ctrl v
winuse mouse-click --x 500 --y 300
```

See [`cli/README.md`](cli/README.md) for the full command list.

## API at a glance

Base URL: `http://<windows-host>:8080`

| Category | Endpoints |
|----------|-----------|
| Health | `GET /health` |
| Windows | `GET /windows`, `GET /windows/active`, `POST /windows/{hwnd}/focus\|minimize\|maximize\|restore` |
| Screenshot | `POST /screenshot` (optional `{"hwnd": 123}`) |
| Mouse | `POST /mouse/move`, `POST /mouse/click` |
| Keyboard | `POST /keyboard/type`, `POST /keyboard/paste`, `POST /keyboard/press` |

All responses:
```json
{ "success": true, "data": { ... }, "error": null }
```

## Agent integration

WinUse ships with a [Moltbot skill](https://github.com/moltbot/moltbot) so any Moltbot agent can drive Windows out of the box. Works with any agent framework that can make HTTP calls — it's just REST.

The standard computer-use loop:
```
Screenshot → Vision model → Decide action → Mouse/Keyboard → Repeat
```

No special SDK, no vendor lock-in, no cloud dependency. Your agent, your Windows box, your rules.

## Why not just use [insert $500/month cloud thing]?

| Approach | Cost | Latency | Control |
|----------|------|---------|---------|
| Mac Mini rack rental | $50-100/mo per machine | 50-200ms (remote) | Limited |
| Cloud browser VM | $0.50-2/hr | 100-500ms | Sandboxed |
| **WinUse on any Windows PC** | **Electricity** | **<10ms (LAN)** | **Full** |

## Configuration

Windows app config: `windows/config.yaml` (created on first run). Override with env vars:

| Variable | Description |
|----------|-------------|
| `WINUSE_API_HOST` | Bind address (default `0.0.0.0`) |
| `WINUSE_API_PORT` | Port (default `8080`) |
| `WINUSE_API_KEY` | API key (none by default) |
| `WINUSE_OUTPUT_DIR` | Screenshot storage path |
| `WINUSE_IMAGE_FORMAT` | `png` or `jpg` |

CLI: set `WINUSE_HOST` (default `http://127.0.0.1:8080`).

## Security model (v1)

No authentication by default. Designed for LAN or trusted environments. If you're exposing this to untrusted networks, add firewall rules or use SSH port forwarding. An API key option exists but isn't enforced in v1.

## Integration test (WSL → Windows)

```bash
# .env at repo root
WINUSE_HOST=http://192.168.1.100:8080
NO_PROXY=*
no_proxy=*
```

```bash
scripts/integration_test_cmd_window.sh
```

Opens Notepad, pastes a timestamp, types a suffix, captures before/after screenshots.

## License

MIT. See `LICENSE`.
