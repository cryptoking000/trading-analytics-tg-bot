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

def main():
    try:
        application = ApplicationBuilder().token(bot_token).build()

        # Add handlers
        application.add_handler(CommandHandler("hello", hello))
        application.add_handler(CommandHandler("help", help))
        application.add_handler(CommandHandler("subscribe", start_payment))
        
        print("👟👟Bot is running...")
        logger.info("Bot is starting...")
        
        # Start the bot with simplified polling
        application.run_polling()
        
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
