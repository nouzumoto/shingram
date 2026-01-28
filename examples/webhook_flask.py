"""
Webhook Bot with Flask - Shingram Example

A bot that uses webhooks with Flask for production deployment.
"""

from shingram import Bot
from flask import Flask, request

bot = Bot("YOUR_BOT_TOKEN")
app = Flask(__name__)

# Create webhook handler
handler = bot.create_webhook_handler(secret_token="your_secret")

@bot.on("command:start")
def handle_start(event):
    bot.send_message(
        chat_id=event.chat_id,
        text="Hey! I'm using shingram\n\nWebhook bot is running!"
    )

@bot.on("message")
def handle_message(event):
    bot.send_message(
        chat_id=event.chat_id,
        text=f"Hey! I'm using shingram\n\nYou said: {event.text}"
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    handler(request.data.decode('utf-8'), dict(request.headers))
    return 'OK'

if __name__ == "__main__":
    # Configure webhook (call once)
    bot.set_webhook(url="https://yourdomain.com/webhook", secret_token="your_secret")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000)
