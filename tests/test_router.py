"""Tests for router."""

import pytest
from shingram.router import Router
from shingram.events import Event


def test_register_handler():
    """Test handler registration."""
    router = Router()
    called = []
    
    def handler(event):
        called.append(event)
    
    router.on("command:start", handler)
    assert "command:start" in router.handlers
    assert len(router.handlers["command:start"]) == 1


def test_register_decorator():
    """Test handler registration as decorator."""
    router = Router()
    called = []
    
    @router.on("command:help")
    def handler(event):
        called.append(event)
    
    assert "command:help" in router.handlers
    assert len(router.handlers["command:help"]) == 1


def test_dispatch_specific():
    """Test dispatching to specific handler."""
    router = Router()
    called = []
    
    def handler(event):
        called.append(event)
    
    router.on("command:start", handler)
    
    event = Event(
        type="command",
        name="start",
        chat_id=123,
        user_id=456,
        text="/start",
        raw={}
    )
    
    router.dispatch(event)
    assert len(called) == 1
    assert called[0] == event


def test_dispatch_type():
    """Test dispatching to type handler."""
    router = Router()
    called = []
    
    def handler(event):
        called.append(event)
    
    router.on("message", handler)
    
    event = Event(
        type="message",
        name="",
        chat_id=123,
        user_id=456,
        text="Hello",
        raw={}
    )
    
    router.dispatch(event)
    assert len(called) == 1
    assert called[0] == event


def test_dispatch_multiple_handlers():
    """Test dispatching to multiple handlers."""
    router = Router()
    called = []
    
    def handler1(event):
        called.append(1)
    
    def handler2(event):
        called.append(2)
    
    router.on("message", handler1)
    router.on("message", handler2)
    
    event = Event(
        type="message",
        name="",
        chat_id=123,
        user_id=456,
        text="Hello",
        raw={}
    )
    
    router.dispatch(event)
    assert len(called) == 2
    assert 1 in called
    assert 2 in called


def test_dispatch_no_handler():
    """Test dispatching when no handler is registered."""
    router = Router()
    
    event = Event(
        type="unknown",
        name="",
        chat_id=123,
        user_id=456,
        text="",
        raw={}
    )
    
    # Should not raise an error
    router.dispatch(event)
