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
    """Sync HTTP client for the Telegram Bot API."""

    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

    def call(self, method: str, **params) -> dict:
        url = f"{self.base_url}/{method}"
        try:
            response = httpx.post(url, json=params, timeout=30.0)
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

    def __getattr__(self, name: str):
        def method(**params):
            return self.call(snake_to_camel(name), **params)
        return method


class AsyncClient:
    """Async HTTP client; same API surface as Client, uses shared parsing."""

    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

    async def call_async(self, method: str, **params):
        url = f"{self.base_url}/{method}"
        async with httpx.AsyncClient() as session:
            try:
                response = await session.post(url, json=params, timeout=30.0)
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

    def __getattr__(self, name: str):
        async def method(**params):
            return await self.call_async(snake_to_camel(name), **params)
        return method
