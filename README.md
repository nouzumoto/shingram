# Shingram

[![Channel](https://shields.io/badge/channel-subscribe-blue?logo=telegram&color=3faee8)](https://t.me/shingramnews)
[![Documentation](https://img.shields.io/badge/docs-here-red)](https://nouzumoto.github.io/shingram/)

Minimal Python wrapper for the Telegram Bot API. **Future-proof**: new API methods work without library updates. **Dual mode**: same code works sync or async. All updates normalized to a single [`Event`](#event-fields) object — no dozens of classes to learn.

### Features

- **Zero hardcoding** — Call any Telegram method; new API features work immediately
- **One Event type** — Every update (message, callback, inline, etc.) has the same shape
- **Sync & Async** — Use `bot.run()` or `bot.run_async()` with the same handlers
- **~1,200 lines** — Lightweight, readable, easy to contribute

## Installation

```bash
pip install shingram
```

## Documentation

Full documentation: **[nouzumoto.github.io/shingram](https://nouzumoto.github.io/shingram/)**

## Quick Start

```python
from shingram import Bot

bot = Bot("YOUR_BOT_TOKEN")

@bot.on("command:start")
def handle_start(event):
    bot.send_message(chat_id=event.chat_id, text="Hello!")

@bot.on("message")
def handle_message(event):
    bot.send_message(chat_id=event.chat_id, text=f"You wrote: {event.text}")

bot.run()
```

## Event types

- **Commands**: `command:start`, `command:help`, etc. Use `command` to catch all commands
- **Messages**: `message` for text messages
- **Edited messages**: `edited_message` for edited text messages
- **Channel posts**: `channel_post` and `edited_channel_post`
- **Inline queries**: `inline_query` for inline search queries
- **Callback queries**: `callback` for inline button clicks
- **Join/Leave events**: `join` and `leave` for group membership changes
- **Poll updates**: `poll` and `poll_answer` for poll-related events
- **Chat member updates**: `chat_member` and `my_chat_member`
- **Chat join requests**: `chat_join_request`
- **Business messages**: `business_message`, `edited_business_message`, `business_connection`
- **Message reactions**: `message_reaction` and `message_reaction_count`
- **Chat boosts**: `chat_boost` and `removed_chat_boost`
- **Shipping and payment**: `shipping_query`, `pre_checkout_query`
- **Chosen inline results**: `chosen_inline_result`

Handlers always get the same `Event`; the field that varies is `type` (and `name` for commands/callbacks).

## Event fields

```python
@dataclass
class Event:
    type: str                    # Event type: "command", "message", "callback", etc.
    name: str                    # Event name: "start" for commands, "" for others
    chat_id: int                 # Chat ID (0 if not applicable)
    user_id: int                 # User ID (0 if not applicable)
    text: str                    # Message text or callback data
    raw: dict                    # Complete raw data from Telegram API
    reply_to: Optional[int]      # ID of replied message (if present)
    chat_type: Optional[str]     # "private", "group", "supergroup", "channel"
    inline_query_id: Optional[str]    # For inline_query events
    callback_query_id: Optional[str]  # For callback_query events
    message_id: Optional[int]    # Message ID (if available)
    username: Optional[str]      # User username (if available)
    first_name: Optional[str]    # User first name (if available)
    chat_title: Optional[str]    # Chat title (for groups/channels)
    last_name: Optional[str]     # User last name (if available)
    language_code: Optional[str] # User language code (if available)
    content_type: Optional[str]  # "text", "photo", "document", etc. (for messages)
```

## Async

Use `async def` handlers and start the bot with `bot.run_async()`. For API calls use `await bot.async_client.send_message(...)` (and the other methods on `bot.async_client`).

```python
from shingram import Bot

bot = Bot("YOUR_BOT_TOKEN")

@bot.on("command:start")
async def handle_start(event):
    await bot.async_client.send_message(chat_id=event.chat_id, text="Hello!")

@bot.on("message")
async def handle_message(event):
    if event.text:
        await bot.async_client.send_message(chat_id=event.chat_id, text=f"You said: {event.text}")

bot.run_async()
```

You can pass optional polling options to `run()` and `run_async()`: `timeout` (default 30), `limit` (default 100), `allowed_updates` (list of update types, or `None` for all), and `on_error` (callback for polling-loop errors, e.g. `bot.run(on_error=logger.exception)`).

## Error Handling

```python
from shingram import Bot, TelegramAPIError

try:
    bot.send_message(chat_id=123, text="Test")
except TelegramAPIError as e:
    print(f"Telegram API error: {e}")
    print(f"Error code: {e.error_code}")
    print(f"Description: {e.description}")
```

## Examples

See the **`examples/`** directory in the repo. You can find plenty of examples there: **sync** (e.g. `echo_bot.py`, `inline_bot.py`, `keyboard_bot.py`, `webhook_flask.py`, `webhook_fastapi.py`) and **async** (e.g. `echo_bot_async.py`, `inline_bot_async.py`, `keyboard_bot_async.py`). Set your bot token in the file and run it.

## License


MIT License - see `LICENSE` for details.
