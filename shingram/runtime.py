"""Runtime for long polling."""

import time
from .client import Client
from .router import Router
from .events import normalize


class Runtime:
    """Runtime that handles long polling."""
    
    def __init__(self, client: Client, router: Router):
        """Initialize runtime with client and router.
        
        Args:
            client: Telegram API client
            router: Event router
        """
        self.client = client
        self.router = router
        self.offset = 0
    
    def run(self):
        """Start the long polling loop."""
        while True:
            try:
                updates = self.client.call(
                    "getUpdates",
                    offset=self.offset,
                    timeout=30
                )
                
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
                print(f"Error in polling loop: {e}")
                time.sleep(1)
