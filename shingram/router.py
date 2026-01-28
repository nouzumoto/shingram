"""Simple event router."""

from typing import Callable, Dict, List
from .events import Event


class Router:
    """Simple router for event handlers."""
    
    def __init__(self):
        """Initialize the router with empty handlers."""
        self.handlers: Dict[str, List[Callable]] = {}
    
    def on(self, event_name: str, handler: Callable = None):
        """Register a handler for an event.
        
        Can be used as a decorator or as a method:
            @router.on("command:start")
            def handler(event):
                ...
                
            router.on("command:start", handler)
        
        Args:
            event_name: Event name pattern (e.g., "command:start", "message")
            handler: Handler function (if None, returns decorator)
        """
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
        """Dispatch an event to registered handlers.
        
        Args:
            event: Event to dispatch
        """
        # Handle wildcard handler "*" first (catches all events)
        if "*" in self.handlers:
            for handler in self.handlers["*"]:
                handler(event)
        
        # Try specific match (e.g., "command:start")
        if event.name:
            specific_name = f"{event.type}:{event.name}"
            if specific_name in self.handlers:
                for handler in self.handlers[specific_name]:
                    handler(event)
                return
        
        # Fall back to type match (e.g., "message")
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                handler(event)
