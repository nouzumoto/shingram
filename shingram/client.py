"""HTTP client for Telegram Bot API."""

import httpx
from .exceptions import TelegramAPIError
from .utils import snake_to_camel


class Client:
    """Client for making requests to Telegram Bot API."""
    
    def __init__(self, token: str):
        """Initialize the client with a bot token.
        
        Args:
            token: Telegram bot token
        """
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    def call(self, method: str, **params) -> dict:
        """Call a Telegram API method.
        
        Args:
            method: API method name in camelCase
            **params: Method parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            TelegramAPIError: If the API returns an error
        """
        url = f"{self.base_url}/{method}"
        
        try:
            response = httpx.post(url, json=params, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                error_code = data.get("error_code", "Unknown")
                description = data.get("description", "Unknown error")
                raise TelegramAPIError(
                    error_code=error_code,
                    description=description,
                    method=method
                )
            
            return data.get("result", {})
        except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            # Timeout is normal for long polling, re-raise as a specific exception
            # that runtime can handle silently
            raise TimeoutError("Long polling timeout (normal)") from e
        except TelegramAPIError:
            # Re-raise TelegramAPIError as-is
            raise
        except httpx.HTTPStatusError as e:
            # HTTP error (4xx, 5xx) - don't expose URL with token
            status_code = e.response.status_code
            try:
                error_data = e.response.json()
                error_code = error_data.get("error_code", status_code)
                description = error_data.get("description", e.response.text[:200])
            except:
                description = f"HTTP {status_code} error"
                error_code = status_code
            
            raise TelegramAPIError(
                error_code=error_code,
                description=description,
                method=method
            )
        except httpx.HTTPError as e:
            # Other HTTP errors (network, etc.) - don't expose URL
            raise TelegramAPIError(
                error_code="HTTP_ERROR",
                description=f"Network error: {type(e).__name__}",
                method=method
            )
    
    def __getattr__(self, name: str):
        """Dynamically create methods for Telegram API calls.
        
        Converts snake_case method names to camelCase API methods.
        
        Example:
            client.send_message(chat_id=123, text="Hello")
            # Calls: client.call("sendMessage", chat_id=123, text="Hello")
        """
        def method(**params):
            camel_method = snake_to_camel(name)
            return self.call(camel_method, **params)
        
        return method
