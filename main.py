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
from recycle import start_dm_service, stop_dm_service
from subscribe import payment_start, button_handler
from callback import address_message_handler
import telegram
from database_function import db
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv
import logging
load_dotenv()
bot_token = os.getenv("bot_token")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        context.user_data['subscribe_input_flag'] = False
        last_active = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("👉start command----")
        # Update user data asynchronously
        db.update_user_data(
            chat_id=update.message.chat_id,
            username=update.message.from_user.username,
            last_active=last_active
        )
        # Get user data asynchronously
        user_data =db.get_user(update.message.chat_id)
        expired_time = user_data.get("expired_time") if user_data else None
        
        if expired_time is None:
            expired_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        current_time = datetime.now()
        expired_time_dt = datetime.strptime(expired_time, '%Y-%m-%d %H:%M:%S')
        is_active = expired_time_dt > current_time
        
        message = (
            "🎉 *Welcome to CryptoAdvisor Bot!*\n\n"
            "I'm here to help you track and analyze cryptocurrencies.\n"
            "I can help you find the best tokens to invest in.\n"
            f"{'Your subscription is active' if is_active else 'Your subscription is expired'}\n"
            f"Your expired time is {expired_time}\n"
            "Run /help to see all available commands."
        )
        
        await update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("👉hello command----")
        user_name = update.message.from_user.first_name
        await update.message.reply_text(f'Hello {user_name}! How can I assist you today?')
    except Exception as e:
        logger.error(f"Error in hello command: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("👉help command----")
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
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

async def start_sendDm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("👉start_sendDm command----")
        await update.message.reply_text("DM service started successfully!")
        await start_dm_service()

    except Exception as e:
        logger.error(f"Error starting DM service: {e}")
        await update.message.reply_text("Failed to start DM service. Please try again later.")

async def stop_sendDm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("👉stop_sendDm command----")
        await stop_dm_service()
        await update.message.reply_text("DM service stopped successfully!")
    except Exception as e:
        logger.error(f"Error stopping DM service: {e}")
        await update.message.reply_text("Failed to stop DM service. Please try again later.")

async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("👉start_payment command----")
        context.user_data['subscribe_input_flag'] = True
        await payment_start(update=update, context=context)
    except Exception as e:
        logger.error(f"Error in payment process: {e}")
        await update.message.reply_text("Payment process failed. Please try again later.")
async def start_recycle(update: Update, context: ContextTypes.DEFAULT_TYPE) ->None:
    try:
        print("👉start_recycle command----")
        await start_dm_service()
        await update.message.reply_text("DM service started successfully!")
    except Exception as e:
        logger.error(f"Error starting DM service: {e}")
        await update.message.reply_text("Failed to start DM service. Please try again later.")
async def stop_recycle(update: Update, context: ContextTypes.DEFAULT_TYPE) ->None:
    try:
        print("👉stop_recycle command----")
        await stop_dm_service()
        await update.message.reply_text("DM service stopped successfully!")
    except Exception as e:
        logger.error(f"Error stopping DM service: {e}")
        await update.message.reply_text("Failed to stop DM service. Please try again later.")
def main():
    try:
        application = ApplicationBuilder().token(bot_token).concurrent_updates(True).build()

        # Add handlers
        application.add_handler(CommandHandler("hello", hello))
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help))
        application.add_handler(CommandHandler("subscribe", start_payment))
        application.add_handler(CommandHandler("startdm", start_sendDm))
        application.add_handler(CommandHandler("stopdm", stop_sendDm))
        application.add_handler(CommandHandler("startrecycle", start_recycle))
        application.add_handler(CommandHandler("stoprecycle", stop_recycle))

        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, address_message_handler))
    
        print("👟👟Bot is running...")
        logger.info("Bot is starting...")
    
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"An error occurred: {e}")

if __name__ == '__main__':
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("Bot stopped by user")
        except Exception as e:
            print(f"Fatal error: {e}")
