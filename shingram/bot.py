"""Bot API: one Router, sync and async clients share the same handlers and Event model."""

import asyncio
from typing import Callable, List, Optional
from .client import Client, AsyncClient
from .router import Router
from .runtime import Runtime, AsyncRuntime
from .webhook import WebhookServer, create_webhook_handler


class Bot:
    """Single bot instance: run() uses sync client, run_async() uses async_client; both use the same router."""

    def __init__(self, token: str):
        self.client = Client(token)
        self.async_client = AsyncClient(token)
        self.router = Router()
        self.runtime = Runtime(self.client, self.router)
        self._webhook_server = None

    def on(self, event_name: str, handler: Optional[Callable] = None):
        """Register handler; decorator or bot.on(name, fn)."""
        return self.router.on(event_name, handler)

    def run(
        self,
        timeout: int = 30,
        limit: int = 100,
        allowed_updates: Optional[List[str]] = None,
        on_error: Optional[Callable[[BaseException], None]] = None,
    ):
        """Long-polling loop (sync). Optional: timeout, limit, allowed_updates, on_error callback."""
        self.runtime.run(
            timeout=timeout,
            limit=limit,
            allowed_updates=allowed_updates,
            on_error=on_error,
        )

    def run_async(
        self,
        timeout: int = 30,
        limit: int = 100,
        allowed_updates: Optional[List[str]] = None,
        on_error: Optional[Callable[[BaseException], None]] = None,
    ):
        """Long-polling loop (async). Handlers can be async; use await bot.async_client.send_message(...) etc."""
        async def _run():
            runtime = AsyncRuntime(self.async_client, self.router)
            await runtime.run_async(
                timeout=timeout,
                limit=limit,
                allowed_updates=allowed_updates,
                on_error=on_error,
            )
        asyncio.run(_run())

    def set_webhook(self, url: str, secret_token: Optional[str] = None, **kwargs):
        params = {"url": url}
        if secret_token:
            params["secret_token"] = secret_token
        params.update(kwargs)
        return self.client.call("setWebhook", **params)

    def delete_webhook(self, drop_pending_updates: bool = False):
        return self.client.call("deleteWebhook", drop_pending_updates=drop_pending_updates)

    def get_webhook_info(self):
        return self.client.call("getWebhookInfo")

    def create_webhook_handler(self, secret_token: Optional[str] = None):
        """Returns a (body, headers) -> bool handler for Flask/FastAPI etc."""
        return create_webhook_handler(self.router, secret_token)

    def handle_webhook_update(self, update_json: dict, headers: Optional[dict] = None, secret_token: Optional[str] = None):
        if not self._webhook_server:
            self._webhook_server = WebhookServer(self.router, secret_token)
        return self._webhook_server.handle_update(update_json, headers)

    def close(self):
        """Close the sync HTTP client."""
        self.client.close()

    async def close_async(self):
        """Close both sync and async HTTP clients."""
        self.client.close()
        await self.async_client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close_async()

    def __getattr__(self, name: str):
        return getattr(self.client, name)
