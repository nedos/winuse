"""Telegram command handlers for WinUse bot."""

from __future__ import annotations

import functools
import io
import logging
import re
import traceback

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import check_user
import winuse_api as api

logger = logging.getLogger(__name__)


def auth(func):
    """Decorator to check user authorization and catch errors."""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not check_user(update.effective_user.id):
            await update.message.reply_text("⛔ Unauthorized")
            return
        try:
            return await func(update, context)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}\n{traceback.format_exc()}")
            msg = update.message or (update.callback_query and update.callback_query.message)
            if msg:
                await msg.reply_text(f"❌ Error: {e}")
    return wrapper


# ---------------------------------------------------------------------------
# /help
# ---------------------------------------------------------------------------

@auth
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🖥️ <b>WinUse Bot</b>\n\n"
        "<b>Windows</b>\n"
        "<code>/windows</code> - List windows\n"
        "<code>/active</code> - Show focused window\n"
        "<code>/focus &lt;title|hwnd&gt;</code> - Focus a window\n"
        "<code>/close &lt;title|hwnd&gt;</code> - Close a window\n\n"
        "<b>Input</b>\n"
        "<code>/key ctrl,n</code> - Press key combo\n"
        "<code>/type hello world</code> - Type text\n"
        "<code>/paste [text]</code> - Paste clipboard\n\n"
        "<b>Mouse</b>\n"
        "<code>/click 500 300</code> - Click at coords\n"
        "<code>/move 500 300</code> - Move cursor\n\n"
        "<b>Other</b>\n"
        "<code>/screenshot</code> - Take screenshot\n"
        "<code>/health</code> - Check WinUse server\n",
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# /windows
# ---------------------------------------------------------------------------

@auth
async def cmd_windows(update: Update, context: ContextTypes.DEFAULT_TYPE):
    windows = await api.list_windows()
    if not windows:
        await update.message.reply_text("🖥️ No windows found")
        return

    # Filter arg
    filter_str = " ".join(context.args) if context.args else None
    if filter_str:
        pat = re.compile(re.escape(filter_str), re.IGNORECASE)
        windows = [w for w in windows if pat.search(w.get("title", ""))]

    if not windows:
        await update.message.reply_text(f"🖥️ No windows matching '{filter_str}'")
        return

    # Build inline buttons (max 20)
    buttons = []
    for w in windows[:20]:
        hwnd = w.get("hwnd", 0)
        title = w.get("title", "?")
        if len(title) > 30:
            title = title[:27] + "..."
        buttons.append([InlineKeyboardButton(
            f"🖥️ {title}",
            callback_data=f"win:{hwnd}",
        )])

    await update.message.reply_text(
        f"🖥️ <b>{len(windows)} Windows</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# ---------------------------------------------------------------------------
# /active
# ---------------------------------------------------------------------------

@auth
async def cmd_active(update: Update, context: ContextTypes.DEFAULT_TYPE):
    w = await api.get_active_window()
    if not w:
        await update.message.reply_text("❌ Could not get active window")
        return
    r = w.get("rect", {})
    await update.message.reply_text(
        f"🖥️ <b>Active Window</b>\n\n"
        f"<b>Title:</b> {w.get('title', '?')}\n"
        f"<b>Process:</b> {w.get('process', '?')}\n"
        f"<b>HWND:</b> <code>{w.get('hwnd', '?')}</code>\n"
        f"<b>Rect:</b> ({r.get('x')}, {r.get('y')}) {r.get('width')}x{r.get('height')}",
        parse_mode="HTML",
    )


# ---------------------------------------------------------------------------
# /focus <title|hwnd>
# ---------------------------------------------------------------------------

@auth
async def cmd_focus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: <code>/focus &lt;title|hwnd&gt;</code>", parse_mode="HTML")
        return

    target = " ".join(context.args)
    hwnd = await _resolve_target(target)
    if hwnd is None:
        await update.message.reply_text(f"❌ No window matching '{target}'")
        return

    ok = await api.focus_window(hwnd)
    await update.message.reply_text(f"{'✅' if ok else '❌'} Focus HWND {hwnd}")


# ---------------------------------------------------------------------------
# /close <title|hwnd>
# ---------------------------------------------------------------------------

@auth
async def cmd_close(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: <code>/close &lt;title|hwnd&gt;</code>", parse_mode="HTML")
        return

    target = " ".join(context.args)
    hwnd = await _resolve_target(target)
    if hwnd is None:
        await update.message.reply_text(f"❌ No window matching '{target}'")
        return

    await api.focus_window(hwnd)
    ok = await api.press_keys(["alt", "f4"])
    await update.message.reply_text(f"{'✅' if ok else '❌'} Closed HWND {hwnd}")


# ---------------------------------------------------------------------------
# /key <combo>
# ---------------------------------------------------------------------------

@auth
async def cmd_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: <code>/key ctrl,n</code>", parse_mode="HTML")
        return

    combo = context.args[0]
    keys = [k.strip().lower() for k in combo.split(",")]
    ok = await api.press_keys(keys)
    await update.message.reply_text(f"{'✅' if ok else '❌'} Pressed {'+'.join(keys)}")


# ---------------------------------------------------------------------------
# /type <text>
# ---------------------------------------------------------------------------

@auth
async def cmd_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: <code>/type hello world</code>", parse_mode="HTML")
        return

    text = " ".join(context.args)
    ok = await api.type_text(text)
    await update.message.reply_text(f"{'✅' if ok else '❌'} Typed {len(text)} chars")


# ---------------------------------------------------------------------------
# /paste [text]
# ---------------------------------------------------------------------------

@auth
async def cmd_paste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else None
    ok = await api.paste_text(text)
    await update.message.reply_text(f"{'✅' if ok else '❌'} Pasted")


# ---------------------------------------------------------------------------
# /click <x> <y>
# ---------------------------------------------------------------------------

@auth
async def cmd_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: <code>/click 500 300</code>", parse_mode="HTML")
        return
    try:
        x, y = int(context.args[0]), int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ x and y must be integers")
        return

    double = len(context.args) > 2 and context.args[2].lower() in ("double", "d", "2")
    ok = await api.mouse_click(x, y, double)
    await update.message.reply_text(f"{'✅' if ok else '❌'} Clicked ({x}, {y}){' [double]' if double else ''}")


# ---------------------------------------------------------------------------
# /move <x> <y>
# ---------------------------------------------------------------------------

@auth
async def cmd_move(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: <code>/move 500 300</code>", parse_mode="HTML")
        return
    try:
        x, y = int(context.args[0]), int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ x and y must be integers")
        return

    ok = await api.mouse_move(x, y)
    await update.message.reply_text(f"{'✅' if ok else '❌'} Moved to ({x}, {y})")


# ---------------------------------------------------------------------------
# /screenshot
# ---------------------------------------------------------------------------

@auth
async def cmd_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Capturing...")
    png = await api.take_screenshot()
    if not png:
        await update.message.reply_text("❌ Screenshot failed")
        return

    await update.message.reply_photo(
        photo=io.BytesIO(png),
        caption="🖥️ Desktop Screenshot",
    )


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

@auth
async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        result = await api.api_get("/health")
        status = result.get("data", {}).get("status", "unknown")
        await update.message.reply_text(f"{'✅' if status == 'ok' else '❌'} WinUse: {status}")
    except Exception as e:
        await update.message.reply_text(f"❌ WinUse unreachable: {e}")


# ---------------------------------------------------------------------------
# Callback handler (inline buttons)
# ---------------------------------------------------------------------------

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not check_user(query.from_user.id):
        await query.answer("Unauthorized", show_alert=True)
        return

    await query.answer()
    data = query.data

    if data.startswith("win:"):
        hwnd = int(data.split(":", 1)[1])
        await _show_window_detail(query, hwnd)
    elif data.startswith("focus:"):
        hwnd = int(data.split(":", 1)[1])
        ok = await api.focus_window(hwnd)
        await query.message.reply_text(f"{'✅' if ok else '❌'} Focused HWND {hwnd}")
    elif data.startswith("close:"):
        hwnd = int(data.split(":", 1)[1])
        await api.focus_window(hwnd)
        ok = await api.press_keys(["alt", "f4"])
        await query.message.reply_text(f"{'✅' if ok else '❌'} Closed HWND {hwnd}")
    elif data.startswith("min:"):
        hwnd = int(data.split(":", 1)[1])
        ok = await api.minimize_window(hwnd)
        await query.message.reply_text(f"{'✅' if ok else '❌'} Minimized HWND {hwnd}")
    elif data.startswith("max:"):
        hwnd = int(data.split(":", 1)[1])
        ok = await api.maximize_window(hwnd)
        await query.message.reply_text(f"{'✅' if ok else '❌'} Maximized HWND {hwnd}")


async def _show_window_detail(query, hwnd: int):
    """Show window details with action buttons."""
    windows = await api.list_windows()
    w = next((w for w in windows if w.get("hwnd") == hwnd), None)
    if not w:
        await query.message.reply_text(f"❌ Window {hwnd} not found")
        return

    r = w.get("rect", {})
    keyboard = [
        [
            InlineKeyboardButton("🎯 Focus", callback_data=f"focus:{hwnd}"),
            InlineKeyboardButton("➖ Min", callback_data=f"min:{hwnd}"),
            InlineKeyboardButton("➕ Max", callback_data=f"max:{hwnd}"),
        ],
        [
            InlineKeyboardButton("❌ Close", callback_data=f"close:{hwnd}"),
        ],
    ]

    await query.message.reply_text(
        f"🖥️ <b>{w.get('title', '?')}</b>\n\n"
        f"<b>Process:</b> {w.get('process', '?')}\n"
        f"<b>HWND:</b> <code>{hwnd}</code>\n"
        f"<b>Rect:</b> ({r.get('x')}, {r.get('y')}) {r.get('width')}x{r.get('height')}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _resolve_target(target: str) -> int | None:
    """Resolve a target string to a window handle (hwnd or title match)."""
    if target.isdigit():
        return int(target)
    w = await api.find_window_by_title(target)
    return w["hwnd"] if w else None
