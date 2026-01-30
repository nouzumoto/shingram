"""Long polling runtimes; both use the same normalize() and Router (shared core)."""

import asyncio
import time
from typing import Callable, List, Optional
from .client import Client, AsyncClient
from .router import Router
from .events import normalize


class Runtime:
    """Sync long-polling loop: getUpdates -> normalize -> dispatch."""

    def __init__(self, client: Client, router: Router):
        self.client = client
        self.router = router
        self.offset = 0

    def run(
        self,
        timeout: int = 30,
        limit: int = 100,
        allowed_updates: Optional[List[str]] = None,
        on_error: Optional[Callable[[BaseException], None]] = None,
    ):
        try:
            while True:
                try:
                    params = {"offset": self.offset, "timeout": timeout, "limit": limit}
                    if allowed_updates is not None:
                        params["allowed_updates"] = allowed_updates
                    updates = self.client.call("getUpdates", **params)
                    if not isinstance(updates, list):
                        updates = []
                    for update in updates:
                        update_id = update.get("update_id")
                        if update_id is not None:
                            self.offset = update_id + 1
                        event = normalize(update)
                        if event:
                            self.router.dispatch(event)
                except KeyboardInterrupt:
                    break
                except TimeoutError:
                    continue
                except Exception as e:
                    if callable(on_error):
                        on_error(e)
                    else:
                        print(f"Error in polling loop: {e}")
                    time.sleep(1)
        finally:
            self.client.close()


class AsyncRuntime:
    """Async long-polling loop; same flow as Runtime, async client and dispatch."""

    def __init__(self, client: AsyncClient, router: Router):
        self.client = client
        self.router = router
        self.offset = 0

    async def run_async(
        self,
        timeout: int = 30,
        limit: int = 100,
        allowed_updates: Optional[List[str]] = None,
        on_error: Optional[Callable[[BaseException], None]] = None,
    ):
        try:
            while True:
                try:
                    params = {"offset": self.offset, "timeout": timeout, "limit": limit}
                    if allowed_updates is not None:
                        params["allowed_updates"] = allowed_updates
                    updates = await self.client.call_async("getUpdates", **params)
                    if not isinstance(updates, list):
                        updates = []
                    for update in updates:
                        update_id = update.get("update_id")
                        if update_id is not None:
                            self.offset = update_id + 1
                        event = normalize(update)
                        if event:
                            await self.router.dispatch_async(event)
                except asyncio.CancelledError:
                    break
                except TimeoutError:
                    continue
                except Exception as e:
                    if callable(on_error):
                        on_error(e)
                    else:
                        print(f"Error in async polling loop: {e}")
                    await asyncio.sleep(1)
        finally:
            await self.client.close()
