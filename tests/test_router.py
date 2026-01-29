"""Tests for router (sync and async dispatch)."""

import asyncio
import pytest
from shingram.router import Router
from shingram.events import Event


def test_register_handler():
    router = Router()
    called = []
    
    def handler(event):
        called.append(event)
    
    router.on("command:start", handler)
    assert "command:start" in router.handlers
    assert len(router.handlers["command:start"]) == 1


def test_register_decorator():
    router = Router()
    called = []
    
    @router.on("command:help")
    def handler(event):
        called.append(event)
    
    assert "command:help" in router.handlers
    assert len(router.handlers["command:help"]) == 1


def test_dispatch_specific():
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
    router = Router()
    event = Event(type="unknown", name="", chat_id=123, user_id=456, text="", raw={})
    router.dispatch(event)


def test_dispatch_async():
    router = Router()
    called = []

    async def handler(event):
        called.append(event)

    router.on("command:start", handler)
    event = Event(type="command", name="start", chat_id=123, user_id=456, text="/start", raw={})

    async def run():
        await router.dispatch_async(event)

    asyncio.run(run())
    assert len(called) == 1
    assert called[0] == event
