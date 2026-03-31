# from telegram import Update
# from telegram.ext import Application, MessageHandler, filters, ContextTypes
# from telegram.request import HTTPXRequest
# from dotenv import load_dotenv
# import httpx
# import os

# load_dotenv()

# GATEWAY_URL = "http://localhost:8000/chat"
# SECRET_KEY = os.getenv("SECRET_KEY")

# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = str(update.effective_user.id)
#     message = update.message.text

#     try:
#         async with httpx.AsyncClient(timeout=60) as client:
#             response = await client.post(
#                 GATEWAY_URL,
#                 json={"user_id": user_id, "message": message},
#                 headers={"x-api-key": SECRET_KEY}
#             )
#             data = response.json()
#             reply = data.get("response", "Something went wrong")

#     except Exception as e:
#         reply = f"Error reaching gateway: {str(e)}"

#     await update.message.reply_text(reply)

# def start_bot():
#     token = os.getenv("TELEGRAM_TOKEN")
    
#     # timeout 
#     request = HTTPXRequest(
#         connection_pool_size=8,
#         read_timeout=60,
#         write_timeout=60,
#         connect_timeout=60,
#         pool_timeout=60
#     )
    
#     app = Application.builder().token(token).request(request).build()
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
#     print("Bot running...")
#     app.run_polling()

# if __name__ == "__main__":
#     start_bot()

from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.database import clear_history
from dotenv import load_dotenv
import httpx
import logging

load_dotenv()

logger = logging.getLogger(__name__)

GATEWAY_URL = "http://localhost:8000/chat"
SECRET_KEY = os.getenv("SECRET_KEY")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! I am NanoClaw, your AI assistant. Ask me anything!")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        clear_history(user_id)
        await update.message.reply_text("History cleard successfully.")
    except Exception as e:
        logger.error(f"Clear failed: {str(e)}")
        await update.message.reply_text("I think something went wrong while clearing history. Try again later.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    message = update.message.text

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                GATEWAY_URL,
                json={"user_id": user_id, "message": message},
                headers={"x-api-key": SECRET_KEY}
            )
            data = response.json()
            reply = data.get("response", "Something went wrong")

    except Exception as e:
        logger.error(f"Gateway error: {str(e)}")
        reply = f"Error reaching gateway: {str(e)}"

    await update.message.reply_text(reply)

def start_bot():
    token = os.getenv("TELEGRAM_TOKEN")

    request = HTTPXRequest(
        connection_pool_size=8,
        read_timeout=60,
        write_timeout=60,
        connect_timeout=60,
        pool_timeout=60
    )

    app = Application.builder().token(token).request(request).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    start_bot()