# WinUse CLI

The WinUse CLI (`winuse`) is a simple, scriptable wrapper around the WinUse Windows API. It can target a local Windows host or a remote Windows machine over LAN.

Project homepage: `github.com/nedos/winuse`

## Install

```bash
pip install winuse-cli
```

## Configure

By default it talks to `http://127.0.0.1:8080`. Override with:

```bash
export WINUSE_HOST="http://192.168.1.100:8080"
```

Or pass `--host` per command.

If you are on WSL or behind a proxy, bypass proxies:

```bash
export NO_PROXY='*'
export no_proxy='*'
```

## Commands

- `health` — check server status
- `windows` — list windows
- `active` — get active window
- `focus <hwnd>`
- `minimize <hwnd>`
- `maximize <hwnd>`
- `restore <hwnd>`
- `screenshot [--hwnd <hwnd>]`
- `mouse-move <x> <y> [--duration <seconds>]`
- `mouse-click [--x <x>] [--y <y>] [--button left|right|middle] [--clicks N]`
- `type <text> [--mode paste|type] [--interval <sec>]`
- `paste <text>`
- `press <key> [key ...]`

## Examples

```bash
winuse health
winuse windows
winuse active
winuse focus 2293790
winuse screenshot
winuse screenshot --hwnd 2293790
winuse type "Hello from WinUse" --mode paste
winuse paste "Привет, Сам"
winuse press ctrl v
winuse mouse-move 10 10 --duration 0.2
winuse mouse-click --x 10 --y 10 --button left --clicks 1
```

## Integration test helper

From repo root:

```bash
scripts/integration_test_cmd_window.sh
```

That script will:
- Open Notepad via Win+R
- Paste a timestamped message
- Refocus the window
- Type a suffix character-by-character
- Capture before/after screenshots

## Tips

- For UTF-8 text, prefer `paste` or `type --mode paste`.
- If a window loses focus, call `focus <hwnd>` before typing.
- The CLI prints JSON responses for scripting.

## License

MIT. See `../LICENSE`.
