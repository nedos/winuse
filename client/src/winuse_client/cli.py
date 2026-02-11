#!/usr/bin/env python3
"""WinUse CLI - Remote Windows desktop automation."""

from __future__ import annotations

import json
import os
import re
import sys

import click
import requests

DEFAULT_URL = "http://localhost:8080"


def normalize_url(raw: str) -> str:
    """Normalize URL input to full http(s)://host:port format.

    Accepts: hostname, hostname:port, IP, IP:port, or full URL.
    Defaults to http scheme and port 8080 when omitted.
    """
    raw = raw.strip().rstrip("/")
    if raw.startswith(("http://", "https://")):
        return raw
    if ":" in raw:
        host, maybe_port = raw.rsplit(":", 1)
        if maybe_port.isdigit():
            return f"http://{raw}"
    return f"http://{raw}:8080"


def _base_url() -> str:
    """Resolve the base URL from env or default, normalized."""
    return normalize_url(os.environ.get("WINUSE_URL", DEFAULT_URL))


def _api_get(base: str, endpoint: str) -> dict:
    try:
        resp = requests.get(f"{base}{endpoint}", timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _api_post(base: str, endpoint: str, data: dict | None = None) -> dict:
    try:
        resp = requests.post(f"{base}{endpoint}", json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _resolve_window(base: str, hwnd: int | None, title: str | None) -> int | None:
    """Resolve a window handle from --hwnd or --title. Returns hwnd or exits."""
    if hwnd:
        return hwnd
    if not title:
        click.echo("Error: provide --hwnd or --title", err=True)
        sys.exit(1)
    windows = _api_get(base, "/windows").get("data", [])
    pattern = re.compile(re.escape(title), re.IGNORECASE)
    matches = [w for w in windows if pattern.search(w.get("title", ""))]
    if not matches:
        click.echo(f"No windows matching '{title}'", err=True)
        sys.exit(1)
    return matches[0]["hwnd"]


def _focus_if(base: str, hwnd: int | None = None, title: str | None = None) -> int | None:
    """Focus a window if hwnd or title is given. Returns resolved hwnd or None."""
    if not hwnd and not title:
        return None
    resolved = _resolve_window(base, hwnd, title)
    _api_post(base, f"/windows/{resolved}/focus")
    return resolved


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
@click.option("--url", "-u", envvar="WINUSE_URL", default=DEFAULT_URL,
              help="WinUse server (hostname, ip:port, or full URL). Env: WINUSE_URL")
@click.version_option(version=__import__("winuse_client").__version__, prog_name="winuse")
@click.pass_context
def cli(ctx: click.Context, url: str) -> None:
    """WinUse - Remote Windows desktop automation CLI."""
    ctx.ensure_object(dict)
    ctx.obj["base"] = normalize_url(url)


def _base(ctx: click.Context) -> str:
    return ctx.obj["base"]


# ---------------------------------------------------------------------------
# Window management
# ---------------------------------------------------------------------------

@cli.command(name="list")
@click.option("--filter", "-f", "title_filter", help="Filter by title (regex)")
@click.pass_context
def list_windows(ctx: click.Context, title_filter: str | None) -> None:
    """List all windows."""
    base = _base(ctx)
    result = _api_get(base, "/windows")
    if not result.get("success"):
        click.echo(f"Error: {result}", err=True)
        return
    windows = result.get("data", [])
    if title_filter:
        pat = re.compile(title_filter, re.IGNORECASE)
        windows = [w for w in windows if pat.search(w.get("title", ""))]

    click.echo(f"{'HWND':>12}  {'Title':<40}  {'Process':<25}  Position")
    click.echo("-" * 105)
    for w in windows:
        r = w.get("rect", {})
        pos = f"({r.get('x',0)}, {r.get('y',0)}) {r.get('width',0)}x{r.get('height',0)}"
        t = w.get("title", "")
        title = (t[:37] + "...") if len(t) > 40 else t
        click.echo(f"{w.get('hwnd',0):>12}  {title:<40}  {w.get('process',''):<25}  {pos}")


@cli.command()
@click.pass_context
def active(ctx: click.Context) -> None:
    """Show the currently focused window."""
    base = _base(ctx)
    result = _api_get(base, "/windows/active")
    if not result.get("success"):
        click.echo(f"Error: {result}", err=True)
        return
    w = result["data"]
    r = w.get("rect", {})
    click.echo(f"HWND:    {w.get('hwnd')}")
    click.echo(f"Title:   {w.get('title')}")
    click.echo(f"Process: {w.get('process')}")
    click.echo(f"Rect:    ({r.get('x')}, {r.get('y')}) {r.get('width')}x{r.get('height')}")


@cli.command()
@click.option("--hwnd", type=int, help="Window handle")
@click.option("--title", "-t", help="Window title (substring match)")
@click.pass_context
def focus(ctx: click.Context, hwnd: int | None, title: str | None) -> None:
    """Focus a window by HWND or title."""
    base = _base(ctx)
    resolved = _resolve_window(base, hwnd, title)
    result = _api_post(base, f"/windows/{resolved}/focus")
    click.echo(f"Focused HWND {resolved}: {result.get('success')}")


@cli.command()
@click.option("--hwnd", type=int, help="Window handle")
@click.option("--title", "-t", help="Window title (substring match)")
@click.pass_context
def minimize(ctx: click.Context, hwnd: int | None, title: str | None) -> None:
    """Minimize a window."""
    base = _base(ctx)
    resolved = _resolve_window(base, hwnd, title)
    _api_post(base, f"/windows/{resolved}/minimize")
    click.echo(f"Minimized HWND {resolved}")


@cli.command()
@click.option("--hwnd", type=int, help="Window handle")
@click.option("--title", "-t", help="Window title (substring match)")
@click.pass_context
def maximize(ctx: click.Context, hwnd: int | None, title: str | None) -> None:
    """Maximize a window."""
    base = _base(ctx)
    resolved = _resolve_window(base, hwnd, title)
    _api_post(base, f"/windows/{resolved}/maximize")
    click.echo(f"Maximized HWND {resolved}")


@cli.command()
@click.option("--hwnd", type=int, help="Window handle")
@click.option("--title", "-t", help="Window title (substring match)")
@click.pass_context
def restore(ctx: click.Context, hwnd: int | None, title: str | None) -> None:
    """Restore a minimized/maximized window."""
    base = _base(ctx)
    resolved = _resolve_window(base, hwnd, title)
    _api_post(base, f"/windows/{resolved}/restore")
    click.echo(f"Restored HWND {resolved}")


@cli.command()
@click.option("--hwnd", type=int, help="Window handle")
@click.option("--title", "-t", help="Window title (substring match)")
@click.pass_context
def close(ctx: click.Context, hwnd: int | None, title: str | None) -> None:
    """Close a window (focus + Alt+F4)."""
    base = _base(ctx)
    resolved = _resolve_window(base, hwnd, title)
    _api_post(base, f"/windows/{resolved}/focus")
    _api_post(base, "/keyboard/press", {"keys": ["alt", "f4"]})
    click.echo(f"Closed HWND {resolved}")


# ---------------------------------------------------------------------------
# Keyboard
# ---------------------------------------------------------------------------

@cli.command(name="key")
@click.argument("combo")
@click.option("--hwnd", type=int, help="Focus this window first")
@click.option("--title", "-t", help="Focus window by title first")
@click.pass_context
def press_key(ctx: click.Context, combo: str, hwnd: int | None, title: str | None) -> None:
    """Press a key combination (e.g. 'ctrl,n' or 'ctrl,shift,esc')."""
    base = _base(ctx)
    _focus_if(base, hwnd, title)
    keys = [k.strip().lower() for k in combo.split(",")]
    result = _api_post(base, "/keyboard/press", {"keys": keys})
    click.echo(f"Pressed {'+'.join(keys)}: {result.get('success')}")


@cli.command(name="type")
@click.argument("text")
@click.option("--hwnd", type=int, help="Focus this window first")
@click.option("--title", "-t", help="Focus window by title first")
@click.pass_context
def type_text(ctx: click.Context, text: str, hwnd: int | None, title: str | None) -> None:
    """Type text into the focused (or specified) window."""
    base = _base(ctx)
    _focus_if(base, hwnd, title)
    result = _api_post(base, "/keyboard/type", {"text": text})
    click.echo(f"Typed: {result.get('success')}")


@cli.command()
@click.option("--hwnd", type=int, help="Focus this window first")
@click.option("--title", "-t", help="Focus window by title first")
@click.option("--text", help="Text to set in clipboard before pasting")
@click.pass_context
def paste(ctx: click.Context, hwnd: int | None, title: str | None, text: str | None) -> None:
    """Paste clipboard content into the focused (or specified) window."""
    base = _base(ctx)
    _focus_if(base, hwnd, title)
    data = {"text": text} if text else {}
    result = _api_post(base, "/keyboard/paste", data)
    click.echo(f"Pasted: {result.get('success')}")


# ---------------------------------------------------------------------------
# Mouse
# ---------------------------------------------------------------------------

@cli.command(name="mouse-click")
@click.argument("x", type=int)
@click.argument("y", type=int)
@click.option("--double", is_flag=True, help="Double-click")
@click.pass_context
def mouse_click(ctx: click.Context, x: int, y: int, double: bool) -> None:
    """Click at screen coordinates."""
    base = _base(ctx)
    data: dict = {"x": x, "y": y}
    if double:
        data["double"] = True
    result = _api_post(base, "/mouse/click", data)
    click.echo(f"Clicked ({x}, {y}){' [double]' if double else ''}: {result.get('success')}")


@cli.command(name="mouse-move")
@click.argument("x", type=int)
@click.argument("y", type=int)
@click.pass_context
def mouse_move(ctx: click.Context, x: int, y: int) -> None:
    """Move the mouse cursor to screen coordinates."""
    base = _base(ctx)
    result = _api_post(base, "/mouse/move", {"x": x, "y": y})
    click.echo(f"Moved to ({x}, {y}): {result.get('success')}")


# ---------------------------------------------------------------------------
# Screenshot
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--output", "-o", help="Save screenshot to local file")
@click.pass_context
def screenshot(ctx: click.Context, output: str | None) -> None:
    """Take a full-desktop screenshot."""
    base = _base(ctx)
    result = _api_post(base, "/screenshot")
    if not result.get("success"):
        click.echo(f"Error: {result}", err=True)
        return

    file_url = result.get("data", {}).get("url", "")
    full_url = f"{base}{file_url}" if file_url.startswith("/") else file_url

    if output:
        resp = requests.get(full_url, timeout=60)
        resp.raise_for_status()
        with open(output, "wb") as f:
            f.write(resp.content)
        click.echo(f"Saved to {output}")
    else:
        click.echo(full_url)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check WinUse server health."""
    base = _base(ctx)
    result = _api_get(base, "/health")
    click.echo(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    cli()


if __name__ == "__main__":
    main()
