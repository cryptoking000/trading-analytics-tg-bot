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
import telegram
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv
import logging
import time
from recylce import start_dm_service, stop_dm_service
load_dotenv()
bot_token = '8006871239:AAH3-qkNrNj6SR3r7hC_Sp3WoLVOlbhg66Q'

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("hello😊")
        user_name = update.message.from_user.first_name
        await update.message.reply_text(f'Hello {user_name}! How can I assist you today?')
    except Exception as e:
        logger.error(f"Error in hello command: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("help👋")
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

async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        context.user_data['subscribe_input_flag'] = True
        print("Processing payment...")
        # Create task for async sleep to not block other operations
        asyncio.create_task(payment_processing(update))
        # Immediately send response while processing continues in background
        await update.message.reply_text("Your payment is being processed. You can continue using other commands.")
    except Exception as e:
        logger.error(f"Error in payment process: {e}")
        await update.message.reply_text("Payment process failed. Please try again later.")

async def payment_processing(update: Update):
    try:
        await asyncio.sleep(10)  # Simulated payment processing
        await update.message.reply_text("Payment processing completed!")
    except Exception as e:
        logger.error(f"Error in payment processing: {e}")

async def start_sendDm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await start_dm_service()
    except Exception as e:
        logger.error(f"Error starting DM service: {e}")
        await update.message.reply_text("Failed to start DM service. Please try again later.")

async def stop_sendDm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await stop_dm_service()
    except Exception as e:
        logger.error(f"Error stopping DM service: {e}")
        await update.message.reply_text("Failed to stop DM service. Please try again later.")

def main():
    try:
        application = ApplicationBuilder().token(bot_token).build()

        # Add handlers
        application.add_handler(CommandHandler("hello", hello))
        application.add_handler(CommandHandler("help", help))
        application.add_handler(CommandHandler("subscribe", start_payment))
        application.add_handler(CommandHandler("startdm", start_sendDm))
        application.add_handler(CommandHandler("stopdm", stop_sendDm))

        print("👟👟Bot is running...")
        
        # Use run_polling without trying to manage the event loop manually
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    # Create a new event loop and run the main function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
    finally:
        loop.close()
