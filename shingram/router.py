"""Event routing: one handler list per pattern; dispatch and dispatch_async use the same matcher."""

import asyncio
from typing import Callable, Dict, List
from .events import Event


class Router:
    """Maps event patterns to handlers; used by both sync and async runtimes."""

    def __init__(self):
        self.handlers: Dict[str, List[Callable]] = {}

    def on(self, event_name: str, handler: Callable = None):
        if handler is None:
            def decorator(func: Callable):
                self._register(event_name, func)
                return func
            return decorator
        
        self._register(event_name, handler)
        return handler
    
    def _register(self, event_name: str, handler: Callable):
        if event_name not in self.handlers:
            self.handlers[event_name] = []
        self.handlers[event_name].append(handler)
    
    def dispatch(self, event: Event):
        if "*" in self.handlers:
            for handler in self.handlers["*"]:
                handler(event)
        
        if event.name:
            specific_name = f"{event.type}:{event.name}"
            if specific_name in self.handlers:
                for handler in self.handlers[specific_name]:
                    handler(event)
                return
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                handler(event)

    async def dispatch_async(self, event: Event):
        """Same matching as dispatch; awaits handlers that are coroutines."""
        if "*" in self.handlers:
            for handler in self.handlers["*"]:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
        if event.name:
            specific_name = f"{event.type}:{event.name}"
            if specific_name in self.handlers:
                for handler in self.handlers[specific_name]:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                return
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
