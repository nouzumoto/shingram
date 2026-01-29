"""Turn raw Telegram updates into Event; used by both sync and async runtimes."""

from dataclasses import dataclass
from typing import Optional


def _message_content_type(message: dict) -> str:
    for key in ("photo", "document", "voice", "video_note", "video", "audio", "sticker", "animation", "location", "contact"):
        if key in message:
            return key
    return "text" if message.get("text") is not None else "text"


@dataclass
class Event:
    """Single shape for all update types; raw payload stays in .raw."""
    type: str
    name: str
    chat_id: int
    user_id: int
    text: str
    raw: dict
    reply_to: Optional[int] = None
    chat_type: Optional[str] = None  # "private", "group", "supergroup", "channel"
    inline_query_id: Optional[str] = None  # For inline_query
    callback_query_id: Optional[str] = None  # For callback_query
    message_id: Optional[int] = None  # Message ID (if available)
    username: Optional[str] = None  # User username (if available)
    first_name: Optional[str] = None  # User first name (if available)
    chat_title: Optional[str] = None  # Chat title (for groups/channels)
    last_name: Optional[str] = None  # User last name (if available)
    language_code: Optional[str] = None  # User language code (if available)
    content_type: Optional[str] = None  # "text", "photo", "document", etc. for messages


def normalize(update_json: dict) -> Optional[Event]:
    """Build one Event from a getUpdates/item or webhook payload; None if unknown type."""
    # Handle message updates
    if "message" in update_json:
        message = update_json["message"]
        chat_id = message.get("chat", {}).get("id")
        
        if "new_chat_members" in message:
            new_members = message.get("new_chat_members", [])
            if new_members:
                member = new_members[0]
                user_id = member.get("id")
                
                if chat_id is None or user_id is None:
                    return None
                
                chat_type = message.get("chat", {}).get("type")
                chat_title = message.get("chat", {}).get("title")
                username = member.get("username")
                first_name = member.get("first_name")
                last_name = member.get("last_name")
                language_code = member.get("language_code")
                return Event(
                    type="join",
                    name="",
                    chat_id=chat_id,
                    user_id=user_id,
                    text="",
                    raw=update_json,
                    reply_to=None,
                    chat_type=chat_type,
                    message_id=message.get("message_id"),
                    username=username,
                    first_name=first_name,
                    chat_title=chat_title,
                    last_name=last_name,
                    language_code=language_code,
                )
        
        if "left_chat_member" in message:
            left_member = message.get("left_chat_member", {})
            user_id = left_member.get("id")
            
            if chat_id is None or user_id is None:
                return None
            
            chat_type = message.get("chat", {}).get("type")
            chat_title = message.get("chat", {}).get("title")
            username = left_member.get("username")
            first_name = left_member.get("first_name")
            last_name = left_member.get("last_name")
            language_code = left_member.get("language_code")
            return Event(
                type="leave",
                name="",
                chat_id=chat_id,
                user_id=user_id,
                text="",
                raw=update_json,
                reply_to=None,
                chat_type=chat_type,
                message_id=message.get("message_id"),
                username=username,
                first_name=first_name,
                chat_title=chat_title,
                last_name=last_name,
                language_code=language_code,
            )
        
        # Handle regular messages and commands
        user = message.get("from")
        user_id = user.get("id") if user else None
        text = message.get("text", "")
        chat_type = message.get("chat", {}).get("type")
        chat_title = message.get("chat", {}).get("title")
        message_id = message.get("message_id")
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        content_type = _message_content_type(message)
        
        if chat_id is None or user_id is None:
            return None
        
        if text.startswith("/"):
            command_parts = text.split()[0][1:].split("@")
            command_name = command_parts[0]
            return Event(
                type="command",
                name=command_name,
                chat_id=chat_id,
                user_id=user_id,
                text=text,
                raw=update_json,
                reply_to=message.get("reply_to_message", {}).get("message_id"),
                chat_type=chat_type,
                message_id=message_id,
                username=username,
                first_name=first_name,
                chat_title=chat_title,
                last_name=last_name,
                language_code=language_code,
                content_type=content_type,
            )
        
        return Event(
            type="message",
            name="",
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            raw=update_json,
            reply_to=message.get("reply_to_message", {}).get("message_id"),
            chat_type=chat_type,
            message_id=message_id,
            username=username,
            first_name=first_name,
            chat_title=chat_title,
            last_name=last_name,
            language_code=language_code,
            content_type=content_type,
        )
    
    if "callback_query" in update_json:
        callback = update_json["callback_query"]
        message = callback.get("message", {})
        chat_id = message.get("chat", {}).get("id") if message else None
        user = callback.get("from", {})
        user_id = user.get("id") if user else None
        data = callback.get("data", "")
        callback_query_id = callback.get("id")
        chat_type = message.get("chat", {}).get("type") if message else None
        chat_title = message.get("chat", {}).get("title") if message else None
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        
        if chat_id is None or user_id is None:
            return None
        
        return Event(
            type="callback",
            name=data.split(":")[0] if ":" in data else data,
            chat_id=chat_id,
            user_id=user_id,
            text=data,
            raw=update_json,
            reply_to=message.get("message_id") if message else None,
            chat_type=chat_type,
            callback_query_id=callback_query_id,
            message_id=message.get("message_id") if message else None,
            username=username,
            first_name=first_name,
            chat_title=chat_title,
            last_name=last_name,
            language_code=language_code,
        )
    
    if "inline_query" in update_json:
        inline = update_json["inline_query"]
        user = inline.get("from", {})
        user_id = user.get("id") if user else None
        query = inline.get("query", "")
        inline_query_id = inline.get("id")
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        
        if user_id is None:
            return None
        
        return Event(
            type="inline_query",
            name="",
            chat_id=0,  # Inline queries don't have chat_id
            user_id=user_id,
            text=query,
            raw=update_json,
            reply_to=None,
            inline_query_id=inline_query_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )
    
    if "edited_message" in update_json:
        message = update_json["edited_message"]
        chat_id = message.get("chat", {}).get("id")
        user = message.get("from")
        user_id = user.get("id") if user else None
        text = message.get("text", "")
        chat_type = message.get("chat", {}).get("type")
        chat_title = message.get("chat", {}).get("title")
        message_id = message.get("message_id")
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        content_type = _message_content_type(message)
        
        if chat_id is None or user_id is None:
            return None
        
        return Event(
            type="edited_message",
            name="",
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            raw=update_json,
            reply_to=message.get("reply_to_message", {}).get("message_id"),
            chat_type=chat_type,
            message_id=message_id,
            username=username,
            first_name=first_name,
            chat_title=chat_title,
            last_name=last_name,
            language_code=language_code,
            content_type=content_type,
        )
    
    if "channel_post" in update_json:
        message = update_json["channel_post"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        chat_type = message.get("chat", {}).get("type")
        chat_title = message.get("chat", {}).get("title")
        message_id = message.get("message_id")
        content_type = _message_content_type(message)
        
        if chat_id is None:
            return None
        
        if text.startswith("/"):
            command_parts = text.split()[0][1:].split("@")
            command_name = command_parts[0]
            return Event(
                type="command",
                name=command_name,
                chat_id=chat_id,
                user_id=0,  # Channel posts don't have from user
                text=text,
                raw=update_json,
                reply_to=message.get("reply_to_message", {}).get("message_id"),
                chat_type=chat_type,
                message_id=message_id,
                chat_title=chat_title,
                content_type=content_type,
            )
        
        return Event(
            type="channel_post",
            name="",
            chat_id=chat_id,
            user_id=0,
            text=text,
            raw=update_json,
            reply_to=message.get("reply_to_message", {}).get("message_id"),
            chat_type=chat_type,
            message_id=message_id,
            chat_title=chat_title,
            content_type=content_type,
        )
    
    if "poll_answer" in update_json:
        poll = update_json["poll_answer"]
        user = poll.get("user", {})
        user_id = user.get("id") if user else None
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        
        if user_id is None:
            return None
        
        return Event(
            type="poll_answer",
            name="",
            chat_id=0,  # Poll answers don't have direct chat_id
            user_id=user_id,
            text="",
            raw=update_json,
            reply_to=None,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )
    
    if "edited_channel_post" in update_json:
        message = update_json["edited_channel_post"]
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        chat_type = message.get("chat", {}).get("type")
        chat_title = message.get("chat", {}).get("title")
        message_id = message.get("message_id")
        content_type = _message_content_type(message)
        
        if chat_id is None:
            return None
        
        if text.startswith("/"):
            command_parts = text.split()[0][1:].split("@")
            command_name = command_parts[0]
            return Event(
                type="command",
                name=command_name,
                chat_id=chat_id,
                user_id=0,
                text=text,
                raw=update_json,
                reply_to=message.get("reply_to_message", {}).get("message_id"),
                chat_type=chat_type,
                message_id=message_id,
                chat_title=chat_title,
                content_type=content_type,
            )
        
        return Event(
            type="edited_channel_post",
            name="",
            chat_id=chat_id,
            user_id=0,
            text=text,
            raw=update_json,
            reply_to=message.get("reply_to_message", {}).get("message_id"),
            chat_type=chat_type,
            message_id=message_id,
            chat_title=chat_title,
            content_type=content_type,
        )
    
    if "chosen_inline_result" in update_json:
        chosen = update_json["chosen_inline_result"]
        user = chosen.get("from", {})
        user_id = user.get("id") if user else None
        result_id = chosen.get("result_id", "")
        query = chosen.get("query", "")
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        
        if user_id is None:
            return None
        
        return Event(
            type="chosen_inline_result",
            name=result_id,
            chat_id=0,
            user_id=user_id,
            text=query,
            raw=update_json,
            reply_to=None,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )
    
    if "shipping_query" in update_json:
        shipping = update_json["shipping_query"]
        user = shipping.get("from", {})
        user_id = user.get("id") if user else None
        query_id = shipping.get("id", "")
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        
        if user_id is None:
            return None
        
        return Event(
            type="shipping_query",
            name=query_id,
            chat_id=0,
            user_id=user_id,
            text="",
            raw=update_json,
            reply_to=None,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )
    
    if "pre_checkout_query" in update_json:
        checkout = update_json["pre_checkout_query"]
        user = checkout.get("from", {})
        user_id = user.get("id") if user else None
        query_id = checkout.get("id", "")
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        
        if user_id is None:
            return None
        
        return Event(
            type="pre_checkout_query",
            name=query_id,
            chat_id=0,
            user_id=user_id,
            text="",
            raw=update_json,
            reply_to=None,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )
    
    if "chat_member" in update_json:
        chat_member = update_json["chat_member"]
        chat = chat_member.get("chat", {})
        chat_id = chat.get("id")
        member = chat_member.get("new_chat_member", {}).get("user", {})
        user_id = member.get("id") if member else None
        chat_type = chat.get("type")
        chat_title = chat.get("title")
        username = member.get("username") if member else None
        first_name = member.get("first_name") if member else None
        last_name = member.get("last_name") if member else None
        language_code = member.get("language_code") if member else None
        
        if chat_id is None or user_id is None:
            return None
        
        status = chat_member.get("new_chat_member", {}).get("status", "")
        
        return Event(
            type="chat_member",
            name=status,
            chat_id=chat_id,
            user_id=user_id,
            text="",
            raw=update_json,
            reply_to=None,
            chat_type=chat_type,
            username=username,
            first_name=first_name,
            chat_title=chat_title,
            last_name=last_name,
            language_code=language_code,
        )
    
    if "my_chat_member" in update_json:
        my_member = update_json["my_chat_member"]
        chat = my_member.get("chat", {})
        chat_id = chat.get("id")
        member = my_member.get("new_chat_member", {}).get("user", {})
        user_id = member.get("id") if member else None
        chat_type = chat.get("type")
        chat_title = chat.get("title")
        username = member.get("username") if member else None
        first_name = member.get("first_name") if member else None
        last_name = member.get("last_name") if member else None
        language_code = member.get("language_code") if member else None
        
        if chat_id is None or user_id is None:
            return None
        
        status = my_member.get("new_chat_member", {}).get("status", "")
        
        return Event(
            type="my_chat_member",
            name=status,
            chat_id=chat_id,
            user_id=user_id,
            text="",
            raw=update_json,
            reply_to=None,
            chat_type=chat_type,
            username=username,
            first_name=first_name,
            chat_title=chat_title,
            last_name=last_name,
            language_code=language_code,
        )
    
    if "chat_join_request" in update_json:
        join_request = update_json["chat_join_request"]
        chat = join_request.get("chat", {})
        chat_id = chat.get("id")
        user = join_request.get("from", {})
        user_id = user.get("id") if user else None
        chat_type = chat.get("type")
        chat_title = chat.get("title")
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        
        if chat_id is None or user_id is None:
            return None
        
        return Event(
            type="chat_join_request",
            name="",
            chat_id=chat_id,
            user_id=user_id,
            text="",
            raw=update_json,
            reply_to=None,
            chat_type=chat_type,
            username=username,
            first_name=first_name,
            chat_title=chat_title,
            last_name=last_name,
            language_code=language_code,
        )
    
    if "business_connection" in update_json:
        business_conn = update_json["business_connection"]
        user = business_conn.get("user", {})
        user_id = user.get("id") if user else None
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        
        if user_id is None:
            return None
        
        return Event(
            type="business_connection",
            name="",
            chat_id=0,
            user_id=user_id,
            text="",
            raw=update_json,
            reply_to=None,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )
    
    if "business_message" in update_json:
        message = update_json["business_message"]
        chat_id = message.get("chat", {}).get("id")
        user = message.get("from")
        user_id = user.get("id") if user else None
        text = message.get("text", "")
        chat_type = message.get("chat", {}).get("type")
        chat_title = message.get("chat", {}).get("title")
        message_id = message.get("message_id")
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        content_type = _message_content_type(message)
        
        if chat_id is None or user_id is None:
            return None
        
        if text.startswith("/"):
            command_parts = text.split()[0][1:].split("@")
            command_name = command_parts[0]
            return Event(
                type="command",
                name=command_name,
                chat_id=chat_id,
                user_id=user_id,
                text=text,
                raw=update_json,
                reply_to=message.get("reply_to_message", {}).get("message_id"),
                chat_type=chat_type,
                message_id=message_id,
                username=username,
                first_name=first_name,
                chat_title=chat_title,
                last_name=last_name,
                language_code=language_code,
                content_type=content_type,
            )
        
        return Event(
            type="business_message",
            name="",
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            raw=update_json,
            reply_to=message.get("reply_to_message", {}).get("message_id"),
            chat_type=chat_type,
            message_id=message_id,
            username=username,
            first_name=first_name,
            chat_title=chat_title,
            last_name=last_name,
            language_code=language_code,
            content_type=content_type,
        )
    
    if "edited_business_message" in update_json:
        message = update_json["edited_business_message"]
        chat_id = message.get("chat", {}).get("id")
        user = message.get("from")
        user_id = user.get("id") if user else None
        text = message.get("text", "")
        chat_type = message.get("chat", {}).get("type")
        chat_title = message.get("chat", {}).get("title")
        message_id = message.get("message_id")
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        content_type = _message_content_type(message)
        
        if chat_id is None or user_id is None:
            return None
        
        return Event(
            type="edited_business_message",
            name="",
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            raw=update_json,
            reply_to=message.get("reply_to_message", {}).get("message_id"),
            chat_type=chat_type,
            message_id=message_id,
            username=username,
            first_name=first_name,
            chat_title=chat_title,
            last_name=last_name,
            language_code=language_code,
            content_type=content_type,
        )
    
    if "deleted_business_messages" in update_json:
        deleted = update_json["deleted_business_messages"]
        chat = deleted.get("chat", {})
        chat_id = chat.get("id")
        chat_type = chat.get("type")
        chat_title = chat.get("title")
        
        if chat_id is None:
            return None
        
        return Event(
            type="deleted_business_messages",
            name="",
            chat_id=chat_id,
            user_id=0,
            text="",
            raw=update_json,
            reply_to=None,
            chat_type=chat_type,
            chat_title=chat_title
        )
    
    if "message_reaction" in update_json:
        reaction = update_json["message_reaction"]
        chat = reaction.get("chat", {})
        chat_id = chat.get("id")
        user = reaction.get("user", {})
        user_id = user.get("id") if user else None
        message_id = reaction.get("message_id")
        chat_type = chat.get("type")
        chat_title = chat.get("title")
        username = user.get("username") if user else None
        first_name = user.get("first_name") if user else None
        last_name = user.get("last_name") if user else None
        language_code = user.get("language_code") if user else None
        
        if chat_id is None or user_id is None:
            return None
        
        return Event(
            type="message_reaction",
            name="",
            chat_id=chat_id,
            user_id=user_id,
            text="",
            raw=update_json,
            reply_to=None,
            chat_type=chat_type,
            message_id=message_id,
            username=username,
            first_name=first_name,
            chat_title=chat_title,
            last_name=last_name,
            language_code=language_code,
        )
    
    if "message_reaction_count" in update_json:
        reaction_count = update_json["message_reaction_count"]
        chat = reaction_count.get("chat", {})
        chat_id = chat.get("id")
        message_id = reaction_count.get("message_id")
        chat_type = chat.get("type")
        chat_title = chat.get("title")
        
        if chat_id is None:
            return None
        
        return Event(
            type="message_reaction_count",
            name="",
            chat_id=chat_id,
            user_id=0,
            text="",
            raw=update_json,
            reply_to=None,
            chat_type=chat_type,
            message_id=message_id,
            chat_title=chat_title
        )
    
    if "poll" in update_json:
        poll = update_json["poll"]
        poll_id = poll.get("id", "")
        
        return Event(
            type="poll",
            name=poll_id,
            chat_id=0,
            user_id=0,
            text="",
            raw=update_json,
            reply_to=None
        )
    
    if "chat_boost" in update_json:
        boost = update_json["chat_boost"]
        chat = boost.get("chat", {})
        chat_id = chat.get("id")
        chat_type = chat.get("type")
        chat_title = chat.get("title")
        
        if chat_id is None:
            return None
        
        return Event(
            type="chat_boost",
            name="",
            chat_id=chat_id,
            user_id=0,
            text="",
            raw=update_json,
            reply_to=None,
            chat_type=chat_type,
            chat_title=chat_title
        )
    
    if "removed_chat_boost" in update_json:
        removed = update_json["removed_chat_boost"]
        chat = removed.get("chat", {})
        chat_id = chat.get("id")
        chat_type = chat.get("type")
        chat_title = chat.get("title")
        
        if chat_id is None:
            return None
        
        return Event(
            type="removed_chat_boost",
            name="",
            chat_id=chat_id,
            user_id=0,
            text="",
            raw=update_json,
            reply_to=None,
            chat_type=chat_type,
            chat_title=chat_title
        )
    
    return None
