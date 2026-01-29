"""
Keyboard Bot (async) - Shingram Example

Custom keyboard and inline buttons with async handlers; same logic as keyboard_bot.
"""

from shingram import Bot

bot = Bot("YOUR_BOT_TOKEN")


@bot.on("command:start")
async def handle_start(event):
    # Reply keyboard (shown under the input field)
    keyboard = {
        "keyboard": [
            [{"text": "Option 1"}, {"text": "Option 2"}],
            [{"text": "Option 3"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True,
    }
    await bot.async_client.send_message(
        chat_id=event.chat_id,
        text="Hey! I'm using shingram\n\nChoose an option or use /buttons for inline buttons!",
        reply_markup=keyboard,
    )


@bot.on("command:buttons")
async def handle_buttons(event):
    # Inline keyboard (buttons attached to the message)
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "Button 1", "callback_data": "btn1"},
                {"text": "Button 2", "callback_data": "btn2"},
            ],
            [{"text": "Button 3", "callback_data": "btn3"}],
        ],
    }
    await bot.async_client.send_message(
        chat_id=event.chat_id,
        text="Hey! I'm using shingram\n\nClick a button:",
        reply_markup=keyboard,
    )


@bot.on("callback")
async def handle_callback(event):
    # Tell Telegram we handled the button press (removes loading state)
    await bot.async_client.answer_callback_query(
        callback_query_id=event.callback_query_id,
        text="Hey! I'm using shingram",
    )
    # event.text holds the callback_data of the pressed button
    if event.text == "btn1":
        await bot.async_client.send_message(
            chat_id=event.chat_id,
            text="Hey! I'm using shingram\n\nYou clicked Button 1!",
        )
    elif event.text == "btn2":
        await bot.async_client.send_message(
            chat_id=event.chat_id,
            text="Hey! I'm using shingram\n\nYou clicked Button 2!",
        )
    elif event.text == "btn3":
        await bot.async_client.send_message(
            chat_id=event.chat_id,
            text="Hey! I'm using shingram\n\nYou clicked Button 3!",
        )


@bot.on("message")
async def handle_message(event):
    # Reply keyboard sends the button label as message text
    if event.text in ["Option 1", "Option 2", "Option 3"]:
        await bot.async_client.send_message(
            chat_id=event.chat_id,
            text=f"Hey! I'm using shingram\n\nYou selected: {event.text}",
        )


if __name__ == "__main__":
    print("Keyboard Bot (async) started. Send /start or /buttons.")
    bot.run_async()
