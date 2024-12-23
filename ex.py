from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.constants import ParseMode
# from recycle import start_dm_service, stop_dm_service
# from subscribe import payment_start, button_handler
# from callback import address_message_handler
import telegram
# from database_function import db
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
import  time
import logging
import tracemalloc
tracemalloc.start()

load_dotenv()
bot_token = os.getenv("bot_token")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("👉hello command----")
        message1 = (
            "👋 *Hello\\!*\n\n"
          
        )
        await update.message.reply_text(text=message1, parse_mode=ParseMode.MARKDOWN)
        

    except Exception as e:
        logger.error(f"Error in hello command: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("👉help command----")
        message = (
           "💚 *help\\!*\n\n"
            
        )
        print("💚",datetime.now())
        await asyncio.sleep(10),
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        print("💚💚",datetime.now())
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await update.message.reply_text("An error occurred. Please try again later.")

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)
async def post_init(application: Application)->None:
    print(f"finished at {time.strftime('%X')}")
    application.add_handler(CommandHandler("hello", hello))
    application.add_handler(CommandHandler("help", help))
def main():
    try:
        application = Application.builder().token(bot_token).concurrent_updates(True).post_init(post_init).build()
        
        print("👟👟Bot is running...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        # # Add handlers
    except Exception as e:
        logger.error(f"Critical error: {e}")
        print(f"An error occurred: {e}")
main()     
