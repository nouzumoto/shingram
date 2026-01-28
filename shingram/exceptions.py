"""Custom exceptions for shingram."""


class ShingramError(Exception):
    """Base exception for all shingram errors."""
    pass


class TelegramAPIError(ShingramError):
    """Raised when Telegram API returns an error.
    
    Attributes:
        error_code: Telegram error code
        description: Error description from Telegram
        method: API method that failed (without token)
    """
    def __init__(self, error_code, description, method=None):
        self.error_code = error_code
        self.description = description
        self.method = method
        super().__init__(f"Telegram API error {error_code}: {description}")


class EventError(ShingramError):
    """Raised when there's an error processing events."""
    pass
