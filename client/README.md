# WinUse Client

Python CLI client for remote Windows desktop automation via the WinUse API.

## Installation

```bash
pip install winuse-client
```

## Configuration

Set the WinUse server URL via environment variable:

```bash
export WINUSE_URL=http://lab:8080
```

Or use the `--url` flag with any command.

The URL can be:
- Hostname: `lab`
- Hostname with port: `lab:9000`
- IP: `192.168.1.100`
- IP with port: `192.168.1.100:8080`
- Full URL: `http://lab:8080`, `https://winuse.example.com`

## Usage

### Window Management

```bash
# List all windows
winuse list

# Focus a window by title (fuzzy match)
winuse focus --title "kimi"
winuse focus --hwnd 329166

# Minimize/Maximize/Restore
winuse minimize --title "notepad"
winuse maximize --hwnd 12345
winuse restore --title "chrome"

# Close a window (Alt+F4)
winuse close --title "kimi"
```

### Keyboard Input

```bash
# Type text
winuse type "Hello, World!"

# Press key combinations
winuse key ctrl,n          # New tab
winuse key ctrl,shift,r    # Rename tab
winuse key alt,f4          # Close window

# Paste from clipboard
winuse paste
```

### Mouse Control

```bash
# Click at coordinates
winuse click 100 200
winuse click 100 200 --double

# Move mouse
winuse move 500 300
```

### Screenshots

```bash
# Take screenshot (full desktop)
winuse screenshot

# Take screenshot with custom filename
winuse screenshot --output ./capture.png
```

### URL Selection

```bash
# Select window by URL/domain pattern
winuse select --url "github.com"
winuse select --title "*chrome*"
```

## Quick Examples

```bash
# Rename a terminal tab in "kimi" window
winuse focus --title "kimi" && winuse key ctrl,shift,r && winuse type "docker" && winuse key enter

# Screenshot a specific window
winuse focus --title "kimi" && winuse screenshot

# Chain multiple commands
winuse focus --title "kimi" --key "ctrl,n" --type "docker" --key "enter"
```

## License

MIT
