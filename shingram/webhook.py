"""Webhook support for Shingram."""

import json
from typing import Callable, Optional
from .router import Router
from .events import normalize


class WebhookServer:
    """Simple webhook server for receiving Telegram updates."""
    
    def __init__(self, router: Router, secret_token: Optional[str] = None):
        """Initialize webhook server.
        
        Args:
            router: Event router to dispatch events to
            secret_token: Optional secret token for webhook validation
        """
        self.router = router
        self.secret_token = secret_token
    
    def handle_update(self, update_json: dict, headers: Optional[dict] = None) -> bool:
        """Handle a single update from webhook.
        
        Args:
            update_json: Update JSON from Telegram
            headers: Optional HTTP headers for validation
            
        Returns:
            True if update was processed successfully
        """
        # Validate secret token if provided
        if self.secret_token:
            if not headers:
                return False
            token_header = headers.get("X-Telegram-Bot-Api-Secret-Token")
            if token_header != self.secret_token:
                return False
        
        # Normalize and dispatch
        event = normalize(update_json)
        if event:
            self.router.dispatch(event)
            return True
        
        return False
    
    def handle_request(self, request_body: str, headers: Optional[dict] = None) -> bool:
        """Handle HTTP request body.
        
        Args:
            request_body: JSON string from HTTP request
            headers: Optional HTTP headers
            
        Returns:
            True if request was processed successfully
        """
        try:
            update_json = json.loads(request_body)
            return self.handle_update(update_json, headers)
        except (json.JSONDecodeError, KeyError):
            return False


def create_webhook_handler(router: Router, secret_token: Optional[str] = None) -> Callable:
    """Create a webhook handler function for use with web frameworks.
    
    Args:
        router: Event router
        secret_token: Optional secret token for validation
        
    Returns:
        Handler function that can be used with Flask, FastAPI, etc.
        
    Example with Flask:
        from flask import Flask, request
        from shingram import Bot
        from shingram.webhook import create_webhook_handler
        
        bot = Bot("TOKEN")
        handler = create_webhook_handler(bot.router)
        
        app = Flask(__name__)
        
        @app.route('/webhook', methods=['POST'])
        def webhook():
            handler(request.data.decode('utf-8'), dict(request.headers))
            return 'OK'
    """
    server = WebhookServer(router, secret_token)
    
    def handler(request_body: str, headers: Optional[dict] = None) -> bool:
        return server.handle_request(request_body, headers)
    
    return handler
