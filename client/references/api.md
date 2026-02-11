# WinUse API Reference

Base URL: `http://<host>:8080`

## Endpoints

### GET /health
Check server health.

**Response:**
```json
{"success": true, "data": "healthy"}
```

### GET /windows
List all windows.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "hwnd": 329166,
      "title": "kimi",
      "process": "WindowsTerminal.exe",
      "pid": 34596,
      "rect": {"x": 1911, "y": 0, "width": 1938, "height": 1053}
    }
  ]
}
```

### GET /windows/active
Get currently focused window.

### POST /windows/{hwnd}/focus
Focus a window by handle.

### POST /windows/{hwnd}/minimize
Minimize window.

### POST /windows/{hwnd}/maximize
Maximize window.

### POST /windows/{hwnd}/restore
Restore minimized window.

### POST /keyboard/type
Type text.

**Body:** `{"text": "Hello World"}`

### POST /keyboard/press
Press key combination.

**Body:** `{"keys": ["ctrl", "shift", "r"]}`

### POST /keyboard/paste
Paste clipboard content.

### POST /mouse/move
Move cursor.

**Body:** `{"x": 500, "y": 300}`

### POST /mouse/click
Click at coordinates.

**Body:** `{"x": 500, "y": 300, "double": false}`

### POST /screenshot
Take screenshot.

**Response:**
```json
{
  "success": true,
  "data": {
    "path": "C:\\winuse\\captures\\capture_xxx.png",
    "url": "/files/capture_xxx.png"
  }
}
```

## Error Responses

```json
{"success": false, "error": "message"}
```
