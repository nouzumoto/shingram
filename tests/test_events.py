"""Tests for event normalization."""

import pytest
from shingram.events import Event, normalize


def test_normalize_command():
    """Test normalization of command updates."""
    update = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {"id": 123, "first_name": "Test"},
            "chat": {"id": 456, "type": "private"},
            "text": "/start",
            "date": 1234567890
        }
    }
    
    event = normalize(update)
    assert event is not None
    assert event.type == "command"
    assert event.name == "start"
    assert event.chat_id == 456
    assert event.user_id == 123
    assert event.text == "/start"


def test_normalize_command_with_botname():
    """Test normalization of command with bot mention."""
    update = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {"id": 123, "first_name": "Test"},
            "chat": {"id": 456, "type": "private"},
            "text": "/start@mybot",
            "date": 1234567890
        }
    }
    
    event = normalize(update)
    assert event is not None
    assert event.name == "start"


def test_normalize_message():
    """Test normalization of regular message updates."""
    update = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {"id": 123, "first_name": "Test"},
            "chat": {"id": 456, "type": "private"},
            "text": "Hello, world!",
            "date": 1234567890
        }
    }
    
    event = normalize(update)
    assert event is not None
    assert event.type == "message"
    assert event.name == ""
    assert event.text == "Hello, world!"


def test_normalize_reply():
    """Test normalization of reply messages."""
    update = {
        "update_id": 1,
        "message": {
            "message_id": 2,
            "from": {"id": 123, "first_name": "Test"},
            "chat": {"id": 456, "type": "private"},
            "text": "This is a reply",
            "reply_to_message": {
                "message_id": 1,
                "from": {"id": 789, "first_name": "Other"},
                "chat": {"id": 456, "type": "private"},
                "text": "Original message"
            },
            "date": 1234567890
        }
    }
    
    event = normalize(update)
    assert event is not None
    assert event.reply_to == 1


def test_normalize_join():
    """Test normalization of join events."""
    update = {
        "update_id": 1,
        "message": {
            "message_id": 1,
            "from": {"id": 123, "first_name": "Test"},
            "chat": {"id": 456, "type": "group"},
            "new_chat_members": [
                {"id": 789, "first_name": "NewUser"}
            ],
            "date": 1234567890
        }
    }
    
    event = normalize(update)
    assert event is not None
    assert event.type == "join"
    assert event.user_id == 789
    assert event.chat_id == 456


def test_normalize_edited_message():
    """Test normalization of edited message updates."""
    update = {
        "update_id": 1,
        "edited_message": {
            "message_id": 1,
            "from": {"id": 123, "first_name": "Test"},
            "chat": {"id": 456, "type": "private"},
            "text": "Edited"
        }
    }
    
    event = normalize(update)
    assert event is not None
    assert event.type == "edited_message"
    assert event.chat_id == 456
    assert event.user_id == 123
    assert event.text == "Edited"


def test_normalize_unsupported():
    """Test that truly unsupported update types return None."""
    # Use an update type that doesn't exist in Telegram API
    update = {
        "update_id": 1,
        "unknown_update_type": {
            "some_field": "value"
        }
    }
    
    event = normalize(update)
    assert event is None
