"""
Inline Bot - Shingram Example

A bot that responds to inline queries with search results.
"""

from shingram import Bot

bot = Bot("YOUR_BOT_TOKEN")

@bot.on("command:start")
def handle_start(event):
    bot.send_message(
        chat_id=event.chat_id,
        text="Hey! I'm using shingram\n\nTry using inline mode: @your_bot_name query"
    )

@bot.on("inline_query")
def handle_inline(event):
    query = event.text.lower()
    
    results = []
    
    if not query or "hello" in query:
        results.append({
            "type": "article",
            "id": "1",
            "title": "Say Hello",
            "description": "Send a greeting message",
            "input_message_content": {
                "message_text": "Hey! I'm using shingram\n\nHello from inline mode!"
            }
        })
    
    if not query or "shingram" in query:
        results.append({
            "type": "article",
            "id": "2",
            "title": "About Shingram",
            "description": "Learn about Shingram",
            "input_message_content": {
                "message_text": "Hey! I'm using shingram\n\nShingram is a minimalist Python library for creating Telegram bots!"
            }
        })
    
    if not query or "help" in query:
        results.append({
            "type": "article",
            "id": "3",
            "title": "Help",
            "description": "Get help",
            "input_message_content": {
                "message_text": "Hey! I'm using shingram\n\nTry searching for: hello, shingram, or help"
            }
        })
    
    if results:
        bot.answer_inline_query(
            inline_query_id=event.inline_query_id,
            results=results
        )

if __name__ == "__main__":
    print("Inline Bot started. Try inline mode: @your_bot_name query")
    bot.run()
