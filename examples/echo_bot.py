"""
Echo Bot - Shingram Example

A simple bot that echoes back messages sent to it.
"""

from shingram import Bot

bot = Bot("YOUR_BOT_TOKEN")

@bot.on("command:start")
def handle_start(event):
    bot.send_message(
        chat_id=event.chat_id,
        text="Hey! I'm using shingram\n\nSend me a message and I'll echo it back!"
    )

@bot.on("message")
def handle_message(event):
    if event.text:
        bot.send_message(
            chat_id=event.chat_id,
            text=f"You said: {event.text}"
        )

if __name__ == "__main__":
    print("Echo Bot started. Send /start to begin.")
    bot.run()
