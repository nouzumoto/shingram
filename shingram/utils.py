"""Utility functions for shingram."""


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase.
    
    Args:
        name: String in snake_case format
        
    Returns:
        String in camelCase format
        
    Examples:
        >>> snake_to_camel("send_message")
        'sendMessage'
        >>> snake_to_camel("get_updates")
        'getUpdates'
    """
    parts = name.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])
