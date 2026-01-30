"""Telegram Bot API client (sync and async share parsing and error handling)."""

import httpx
from .exceptions import TelegramAPIError
from .utils import snake_to_camel


def _result_or_raise(data: dict, method: str):
    """Shared: turn API JSON into result or raise TelegramAPIError."""
    if data.get("ok"):
        return data.get("result", {})
    raise TelegramAPIError(
        error_code=data.get("error_code", "Unknown"),
        description=data.get("description", "Unknown error"),
        method=method,
    )


def _error_from_http_response(response, method: str):
    """Shared: build TelegramAPIError from failed HTTP response."""
    try:
        body = response.json()
        code = body.get("error_code", response.status_code)
        desc = body.get("description", response.text[:200])
    except Exception:
        code = response.status_code
        desc = f"HTTP {response.status_code} error"
    return TelegramAPIError(error_code=code, description=desc, method=method)


class Client:
    """Sync HTTP client for the Telegram Bot API with persistent session."""

    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self._client = httpx.Client()

    def call(self, method: str, **params) -> dict:
        url = f"{self.base_url}/{method}"
        try:
            response = self._client.post(url, json=params, timeout=30.0)
            response.raise_for_status()
            return _result_or_raise(response.json(), method)
        except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            raise TimeoutError("Long polling timeout (normal)") from e
        except TelegramAPIError:
            raise
        except httpx.HTTPStatusError as e:
            raise _error_from_http_response(e.response, method)
        except httpx.HTTPError as e:
            raise TelegramAPIError(
                error_code="HTTP_ERROR",
                description=f"Network error: {type(e).__name__}",
                method=method,
            )

    def close(self):
        """Close the HTTP session."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __getattr__(self, name: str):
        def method(**params):
            return self.call(snake_to_camel(name), **params)
        return method


class AsyncClient:
    """Async HTTP client with persistent session; same API surface as Client."""

    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Lazy initialization of the HTTP session."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient()
        return self._client

    async def call_async(self, method: str, **params):
        url = f"{self.base_url}/{method}"
        client = await self._get_client()
        try:
            response = await client.post(url, json=params, timeout=30.0)
            response.raise_for_status()
            return _result_or_raise(response.json(), method)
        except (httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            raise TimeoutError("Long polling timeout (normal)") from e
        except TelegramAPIError:
            raise
        except httpx.HTTPStatusError as e:
            raise _error_from_http_response(e.response, method)
        except httpx.HTTPError as e:
            raise TelegramAPIError(
                error_code="HTTP_ERROR",
                description=f"Network error: {type(e).__name__}",
                method=method,
            )

    async def close(self):
        """Close the HTTP session."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    def __getattr__(self, name: str):
        async def method(**params):
            return await self.call_async(snake_to_camel(name), **params)
        return method
