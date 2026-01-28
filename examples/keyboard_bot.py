"""
Keyboard Bot - Shingram Example

A bot that demonstrates custom keyboards and inline buttons.
"""

from shingram import Bot

bot = Bot("YOUR_BOT_TOKEN")

@bot.on("command:start")
def handle_start(event):
    # Custom reply keyboard
    keyboard = {
        "keyboard": [
            [{"text": "Option 1"}, {"text": "Option 2"}],
            [{"text": "Option 3"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
    
    bot.send_message(
        chat_id=event.chat_id,
        text="Hey! I'm using shingram\n\nChoose an option from the keyboard or use /buttons for inline buttons!",
        reply_markup=keyboard
    )

@bot.on("command:buttons")
def handle_buttons(event):
    # Inline keyboard
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "Button 1", "callback_data": "btn1"},
                {"text": "Button 2", "callback_data": "btn2"}
            ],
            [
                {"text": "Button 3", "callback_data": "btn3"}
            ]
        ]
    }
    
    bot.send_message(
        chat_id=event.chat_id,
        text="Hey! I'm using shingram\n\nClick a button:",
        reply_markup=keyboard
    )

@bot.on("callback")
def handle_callback(event):
    # Answer the callback query
    bot.answer_callback_query(
        callback_query_id=event.callback_query_id,
        text="Hey! I'm using shingram"
    )
    
    # Handle different button clicks
    if event.text == "btn1":
        bot.send_message(
            chat_id=event.chat_id,
            text="Hey! I'm using shingram\n\nYou clicked Button 1!"
        )
    elif event.text == "btn2":
        bot.send_message(
            chat_id=event.chat_id,
            text="Hey! I'm using shingram\n\nYou clicked Button 2!"
        )
    elif event.text == "btn3":
        bot.send_message(
            chat_id=event.chat_id,
            text="Hey! I'm using shingram\n\nYou clicked Button 3!"
        )

@bot.on("message")
def handle_message(event):
    # Handle keyboard button presses
    if event.text in ["Option 1", "Option 2", "Option 3"]:
        bot.send_message(
            chat_id=event.chat_id,
            text=f"Hey! I'm using shingram\n\nYou selected: {event.text}"
        )

if __name__ == "__main__":
    print("Keyboard Bot started. Send /start to see the keyboard, or /buttons for inline buttons.")
    bot.run()
