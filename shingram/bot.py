"""Main Bot class - public API."""

from typing import Callable, Optional
from .client import Client
from .router import Router
from .runtime import Runtime
from .webhook import WebhookServer, create_webhook_handler


class Bot:
    """Main bot class - public API for shingram."""
    
    def __init__(self, token: str):
        """Initialize the bot with a token.
        
        Args:
            token: Telegram bot token
        """
        self.client = Client(token)
        self.router = Router()
        self.runtime = Runtime(self.client, self.router)
        self._webhook_server = None
    
    def on(self, event_name: str, handler: Optional[Callable] = None):
        """Register an event handler.
        
        Can be used as a decorator or as a method:
            @bot.on("command:start")
            def handler(event):
                ...
                
            bot.on("command:start", handler)
        
        Args:
            event_name: Event name pattern
            handler: Handler function (if None, returns decorator)
        """
        return self.router.on(event_name, handler)
    
    def run(self):
        """Start the bot (begin long polling)."""
        self.runtime.run()
    
    def set_webhook(self, url: str, secret_token: Optional[str] = None, **kwargs):
        """Set webhook URL for receiving updates.
        
        Args:
            url: Webhook URL
            secret_token: Optional secret token for webhook validation
            **kwargs: Additional parameters (certificate, ip_address, etc.)
        """
        params = {"url": url}
        if secret_token:
            params["secret_token"] = secret_token
        params.update(kwargs)
        return self.client.call("setWebhook", **params)
    
    def delete_webhook(self, drop_pending_updates: bool = False):
        """Delete webhook.
        
        Args:
            drop_pending_updates: If True, drop pending updates
        """
        return self.client.call("deleteWebhook", drop_pending_updates=drop_pending_updates)
    
    def get_webhook_info(self):
        """Get current webhook information."""
        return self.client.call("getWebhookInfo")
    
    def create_webhook_handler(self, secret_token: Optional[str] = None):
        """Create a webhook handler function for use with web frameworks.
        
        Args:
            secret_token: Optional secret token for validation
            
        Returns:
            Handler function that can be used with Flask, FastAPI, etc.
            
        Example with Flask:
            from flask import Flask, request
            from shingram import Bot
            
            bot = Bot("TOKEN")
            handler = bot.create_webhook_handler()
            
            @bot.on("message")
            def handle_message(event):
                bot.send_message(chat_id=event.chat_id, text="Hello!")
            
            app = Flask(__name__)
            
            @app.route('/webhook', methods=['POST'])
            def webhook():
                handler(request.data.decode('utf-8'), dict(request.headers))
                return 'OK'
        """
        return create_webhook_handler(self.router, secret_token)
    
    def handle_webhook_update(self, update_json: dict, headers: Optional[dict] = None, secret_token: Optional[str] = None):
        """Handle a single webhook update.
        
        Args:
            update_json: Update JSON from Telegram
            headers: Optional HTTP headers for validation
            secret_token: Optional secret token for validation
        """
        if not self._webhook_server:
            self._webhook_server = WebhookServer(self.router, secret_token)
        return self._webhook_server.handle_update(update_json, headers)
    
    def __getattr__(self, name: str):
        """Delegate dynamic API calls to client.
        
        Allows calling any Telegram API method:
            bot.send_message(chat_id=123, text="Hello")
        """
        return getattr(self.client, name)
