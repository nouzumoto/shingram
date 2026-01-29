"""
Echo Bot (async) - Shingram Example

Echo bot with async handlers. Use await bot.async_client.send_message(...); start with bot.run_async().
"""

from shingram import Bot

bot = Bot("YOUR_BOT_TOKEN")


@bot.on("command:start")
async def handle_start(event):
    await bot.async_client.send_message(
        chat_id=event.chat_id,
        text="Hey! I'm using shingram\n\nSend me a message and I'll echo it back!",
    )


@bot.on("message")
async def handle_message(event):
    if event.text:
        await bot.async_client.send_message(
            chat_id=event.chat_id,
            text=f"You said: {event.text}",
        )


if __name__ == "__main__":
    print("Echo Bot (async) started. Send /start to begin.")
    bot.run_async()
