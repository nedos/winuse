"""
WinUse Telegram Bot - Remote Windows desktop control via Telegram.

Uses python-telegram-bot with webhook mode behind FastAPI.
"""

import logging
import sys

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, WEBHOOK_URL, PORT, WINUSE_BASE, MODE
from commands import (
    cmd_help,
    cmd_windows,
    cmd_active,
    cmd_focus,
    cmd_close,
    cmd_key,
    cmd_type,
    cmd_paste,
    cmd_click,
    cmd_move,
    cmd_screenshot,
    cmd_health,
    handle_callback,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def handle_message(update: Update, context):
    """Log unhandled messages."""
    if update.message and update.message.chat:
        chat = update.message.chat
        title = chat.title or chat.username or chat.first_name or "DM"
        logger.info(f"Message in {chat.type}: '{title}' (ID: {chat.id})")


def main():
    logger.info("Starting WinUse Telegram Bot")
    logger.info(f"WinUse server: {WINUSE_BASE}")
    logger.info(f"Webhook URL: {WEBHOOK_URL}")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("start", cmd_help))
    application.add_handler(CommandHandler("windows", cmd_windows))
    application.add_handler(CommandHandler("active", cmd_active))
    application.add_handler(CommandHandler("focus", cmd_focus))
    application.add_handler(CommandHandler("close", cmd_close))
    application.add_handler(CommandHandler("key", cmd_key))
    application.add_handler(CommandHandler("type", cmd_type))
    application.add_handler(CommandHandler("paste", cmd_paste))
    application.add_handler(CommandHandler("click", cmd_click))
    application.add_handler(CommandHandler("move", cmd_move))
    application.add_handler(CommandHandler("screenshot", cmd_screenshot))
    application.add_handler(CommandHandler("health", cmd_health))

    # Callback query handler (inline buttons)
    application.add_handler(CallbackQueryHandler(handle_callback))

    # Catch-all message logger
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    if MODE == "webhook" and WEBHOOK_URL:
        logger.info(f"Running in webhook mode on port {PORT}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=f"winuse/webhook/{TELEGRAM_BOT_TOKEN}",
            webhook_url=f"{WEBHOOK_URL}/webhook/{TELEGRAM_BOT_TOKEN}",
            allowed_updates=Update.ALL_TYPES,
        )
    else:
        logger.info("Running in polling mode")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
