# Shingram

A minimalist Python library for creating Telegram bots with zero hardcoding and automatic API method support.

Shingram provides a lightweight wrapper for the Telegram Bot API, designed to be simple, powerful, and future-proof. The library automatically supports all Telegram API methods without requiring code updates when new methods are added.

📖 **[Documentation](https://nouzumoto.github.io/shingram/)**

## Features

- **Zero hardcoding**: All Telegram API methods work automatically without library updates
- **Automatic conversion**: Python-style `snake_case` method names are automatically converted to Telegram's `camelCase` format
- **Event normalization**: All Telegram updates are normalized into a consistent `Event` object format
- **Complete update coverage**: Supports all Telegram Bot API update types
- **Simple API**: Register handlers with decorators or direct method calls
- **Automatic long polling**: Built-in offset management and error handling
- **Full raw data access**: Complete access to original Telegram API data via `event.raw`
- **Synchronous**: No async complexity - simple, linear code

## Installation

```bash
pip install shingram
```

## Documentation

Full documentation is available at: **[https://nouzumoto.github.io/shingram/](https://nouzumoto.github.io/shingram/)**

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

## Event Types

Shingram normalizes all Telegram updates into consistent `Event` objects. Supported event types include:

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

All events are normalized into the same `Event` format for consistency.

## Event Object

Every handler receives an `Event` object with the following fields:

```python
@dataclass
class Event:
    type: str                    # Event type: "command", "message", "callback", etc.
    name: str                   # Event name: "start" for commands, "" for others
    chat_id: int                # Chat ID (0 if not applicable)
    user_id: int                # User ID (0 if not applicable)
    text: str                   # Message text or callback data
    raw: dict                   # Complete raw data from Telegram API
    reply_to: Optional[int]      # ID of replied message (if present)
    chat_type: Optional[str]     # "private", "group", "supergroup", "channel"
    inline_query_id: Optional[str]    # For inline_query events
    callback_query_id: Optional[str]  # For callback_query events
    message_id: Optional[int]    # Message ID (if available)
    username: Optional[str]      # User username (if available)
    first_name: Optional[str]    # User first name (if available)
    chat_title: Optional[str]    # Chat title (for groups/channels)
```

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

See the `examples/` directory for complete working examples:
- `echo_bot.py` - Simple echo bot that repeats messages
- `inline_bot.py` - Inline query bot with search functionality
- `keyboard_bot.py` - Bot with custom keyboard and inline buttons
- `webhook_flask.py` - Webhook example using Flask
- `webhook_fastapi.py` - Webhook example using FastAPI

## License

MIT License - see `LICENSE` for details.