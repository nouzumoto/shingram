"""Tests for event normalization."""

import pytest
from shingram.events import Event, normalize


def test_normalize_command():
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
    update = {
        "update_id": 1,
        "unknown_update_type": {
            "some_field": "value"
        }
    }
    
    event = normalize(update)
    assert event is None
