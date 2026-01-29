"""
Webhook Bot with FastAPI - Shingram Example

A bot that uses webhooks with FastAPI for production deployment.
"""

from shingram import Bot
from fastapi import FastAPI, Request

bot = Bot("YOUR_BOT_TOKEN")
app = FastAPI()
# Handler receives (body, headers); call it from your webhook route
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

@app.post('/webhook')
async def webhook(request: Request):
    body = await request.body()
    handler(body.decode('utf-8'), dict(request.headers))
    return {"status": "ok"}

if __name__ == "__main__":
    # Point Telegram to this URL (do once, or after changing URL)
    bot.set_webhook(url="https://yourdomain.com/webhook", secret_token="your_secret")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
