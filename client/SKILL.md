---
name: winuse-client
description: Python CLI client for remote Windows desktop automation via the WinUse API. Use when working with WinUse to control Windows machines remotely - listing windows, focusing windows, sending keyboard/mouse input, taking screenshots, and automating GUI interactions.
---

# WinUse Client

Python CLI client for remote Windows desktop automation via the WinUse API.

## Quick Start

Install the client:

```bash
cd ~/dev/winuse-client
pip install -e . --break-system-packages
```

Set the WinUse server URL:

```bash
export WINUSE_URL=lab          # hostname
export WINUSE_URL=lab:8080     # hostname with port
export WINUSE_URL=192.168.1.100:8080  # IP with port
```

Or use `--url` with any command.

## Common Operations

### List Windows

```bash
winuse list                           # All windows
winuse list --filter "Terminal"       # Filter by title
```

### Focus Windows

```bash
winuse focus --hwnd 329166            # By handle
winuse focus --title "kimi"           # By title (fuzzy match)
```

### Send Input

```bash
# Type text
winuse type "Hello World" --title "notepad"

# Press key combinations
winuse key ctrl,n --title "kimi"      # New tab
winuse key ctrl,shift,r               # Rename tab
winuse key alt,f4                     # Close window

# Paste clipboard
winuse paste --title "kimi"
```

### Mouse Control

```bash
winuse mouse_click 500 300            # Click at coordinates
winuse mouse_click 500 300 --double   # Double-click
winuse move 500 300                   # Move cursor
```

### Screenshots

```bash
winuse screenshot                     # URL to screenshot
winuse screenshot -o ./capture.png    # Save to file
```

### Window Management

```bash
winuse minimize --hwnd 329166
winuse maximize --title "kimi"
winuse restore --hwnd 329166
winuse close --title "notepad"        # Alt+F4
```

## Chaining Operations

Use `send` for multiple operations on one window:

```bash
winuse send --title "kimi" --keys "ctrl,n" --text "docker" --keys "enter"
```

## URL Format

The `--url` flag and `WINUSE_URL` env var accept:
- Hostname: `lab`
- Hostname:port: `lab:9000`
- IP: `192.168.1.100`
- IP:port: `192.168.1.100:8080`
- Full URL: `http://lab:8080`, `https://winuse.example.com`

Default port is 8080 if not specified.

## Reference

See `references/api.md` for complete API endpoint documentation.
