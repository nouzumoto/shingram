"""Shingram - A minimal Telegram bot API wrapper."""

from .bot import Bot
from .exceptions import ShingramError, TelegramAPIError, EventError
from .webhook import WebhookServer, create_webhook_handler

__all__ = [
    "Bot",
    "ShingramError",
    "TelegramAPIError",
    "EventError",
    "WebhookServer",
    "create_webhook_handler",
]
__version__ = "0.3.0"
