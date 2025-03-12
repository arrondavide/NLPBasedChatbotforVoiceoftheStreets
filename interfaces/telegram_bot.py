from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from backend.logic import process_message
import os
from dotenv import load_dotenv

load_dotenv()

def start(update, context):
    update.message.reply_text("Welcome to Voice of the Streets! Report issues like 'Power outage in Colombo'.")

def handle_message(update, context):
    message = update.message.text
    user_id = update.message.from_user.id
    response = process_message(message, "telegram", str(user_id))
    update.message.reply_text(response)

def main():
    updater = Updater(os.getenv("TELEGRAM_TOKEN"), use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()