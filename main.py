from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.constants import ParseMode
from sendDM import start_dm_service, stop_dm_service
from subscribe import payment_start, button_handler
from callback import address_message_handler
import telegram
from database_function import db
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
bot_token = os.getenv("bot_token")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['subscribe_input_flag'] = False
    last_active = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.update_user_data(chat_id=update.message.chat_id, username=update.message.from_user.username, last_active=last_active)
    expired_time =db.get_user(update.message.chat_id).get("expired_time")
    if expired_time is None:
        expired_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = (
        "🎉 *Welcome to CryptoAdvisor Bot!*\n\n"
        "I'm here to help you track and analyze cryptocurrencies.\n"
        "I can help you find the best tokens to invest in.\n"
        f"{'Your subscription is active' if expired_time > datetime.now().strftime('%Y-%m-%d %H:%M:%S') else 'Your subscription is expired'}\n"
        f"your expired time is {expired_time}\n"
        "Run /help to see all available commands."
    )
    await update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.message.from_user.first_name
    await update.message.reply_text(f'Hello {user_name}! How can I assist you today?')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
        "🤖 *Welcome to CryptoAdvisor Bot!*\n\n"
        "I am your AI-powered cryptocurrency market assistant. Here's what I can do for you:\n\n"
        "📊 *Key Features:*\n"
        "• Real-time cryptocurrency analysis and monitoring\n"
        "• Market trend detection and insights\n" 
        "• Detailed metrics including market cap, volume, ATH\n"
        "• AI-powered price movement predictions\n"
        "• Premium features available via subscription\n\n"
        "🔍 *Available Commands:*\n"
        "• /start - Begin interaction\n"
        "• /hello - Get a greeting\n"
        "• /help - Show this help message\n"
        "• /subscribe - Access premium features\n\n"
        "Simply send me a token address to get detailed analytics!"
    )
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

async def start_sendDm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start_dm_service()
async def stop_sendDm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await stop_dm_service()

async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['subscribe_input_flag'] = True
    await payment_start(update=update, context=context)

async def main():
    # Load bot token from environment variable or config file in production
    application = ApplicationBuilder().token(bot_token).build()

    # Add handlers
    application.add_handler(CommandHandler("hello", hello))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("subscribe", start_payment))
    application.add_handler(CommandHandler("start_sendDm", start_sendDm))
    application.add_handler(CommandHandler("stop_sendDm", stop_sendDm))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, address_message_handler))
    
    print("👟👟Bot is running...")
    
    try:
        application.run_polling(drop_pending_updates=True)
    except telegram.error.TimedOut:
        print("Connection timed out. Please check your internet connection and try again.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
if __name__ == '__main__':
    asyncio.run(main())
