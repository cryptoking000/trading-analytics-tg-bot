import asyncio
import telegram
from telegram.constants import ParseMode

from database_function import db
import os
from dotenv import load_dotenv
from ai_insight import ai_insight
from pymongo import MongoClient
from datetime import datetime

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri)
mongodb = mongo_client["telegram_bot_db"]
token_collection = mongodb["token_contracts"]
TOKEN = os.getenv("bot_token")

URL_TELEGRAM_BASE = f'https://api.telegram.org/bot{TOKEN}'
URL_GET_UPDATES = f'{URL_TELEGRAM_BASE}/getUpdates'

# Flag to control the DM service
dm_task = None

async def send_message(text, chat_id, parse_mode=ParseMode.MARKDOWN):
    try:
        temp_bot = telegram.Bot(token=TOKEN)
        await temp_bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        return True
    except telegram.error.TelegramError as e:
        print(f"Failed to send message to {chat_id}: {str(e)}")
        if "Forbidden: bot was blocked by the user" in str(e):
            db.delete_user(chat_id)
            print(f"Deleted blocked user {chat_id}")
      
        return False

async def send_dm():
    try:
        users = db.get_all_users()
        processed_chat_ids = set()

        if not users:
            print("No users found in database.")
            return

        ai_insight_text = await ai_insight()

        for user in users:
            chat_id = user.get('chat_id')
            if not chat_id:
                print(f"Invalid chat_id for user: {user}")
                continue
                
            db.update_is_paid_state(chat_id)
            is_paid = user.get('is_paid', False)
            username = user.get('username', 'User')
            
            if chat_id not in processed_chat_ids:
                first_message = await send_message("🤔 Processing your request, please wait...", chat_id=chat_id)
                message = (
                    f"Hello {username}!\n\n"
                    f"{' Thank you for being our premium member!' if is_paid else '💫 Upgrade to premium for more features!'}\n"
                    f"{ai_insight_text if is_paid else ''}\n"
                    f"Use /help to see available commands."
                )
                if is_paid:
                    if await send_message(text=message, chat_id=chat_id):
                        await first_message.remove()
                        processed_chat_ids.add(chat_id)
                        print(f"Successfully sent message to {username} (ID: {chat_id})")
                    else:
                        print(f"Failed to send message to {username} (ID: {chat_id})")
                   
            
    except Exception as e:
        print(f"Error in send_dm: {str(e)}")

async def stop_dm_service():
    global dm_task
    if dm_task:
        dm_task.cancel()
        try:
            await dm_task
        except asyncio.CancelledError:
            pass
        dm_task = None
    print("DM service stopped successfully")

async def periodic_dm():
    while True:
        try:
           
            
            print("👇👇👇Periodic DM service starting...")
            await send_dm()
            await asyncio.sleep(300)  # 5 minutes interval
            print(f"Last run: {datetime.now()}")
            
        except asyncio.CancelledError:
            print("DM service cancelled")
            break
        except Exception as e:
            print(f"Error in DM service: {str(e)}")
            await asyncio.sleep(50)

async def start_dm_service():
    global dm_task
    if dm_task is None:
        print("DM service starting...")
        dm_task = asyncio.create_task(periodic_dm())
    else:
        print("DM service is already running")
# async def start_recycle(update: Update, context: ContextTypes.DEFAULT_TYPE) ->None:
#     try:
#         print("👉start_recycle command----")
#         await start_dm_service()
#         await update.message.reply_text("DM service started successfully!")
#     except Exception as e:
#         print(f"Error starting DM service: {e}")
#         await update.message.reply_text("Failed to start DM service. Please try again later.")
# async def stop_recycle(update: Update, context: ContextTypes.DEFAULT_TYPE) ->None:
#     try:
#         print("👉stop_recycle command----")
#         await stop_dm_service()
#         await update.message.reply_text("DM service stopped successfully!")
#     except Exception as e:
#         print(f"Error stopping DM service: {e}")
#         await update.message.reply_text("Failed to stop DM service. Please try again later.")
# if __name__ == "__main__":
#     try:
#         print("👉recycle running----")
#         application = ApplicationBuilder().token(TOKEN).concurrent_updates(True).build()

#         application.add_handler(CommandHandler("startrecycle", start_recycle))
#         application.add_handler(CommandHandler("stoprecycle", stop_recycle))
#         application.run_polling(allowed_updates=Update.ALL_TYPES)
        
#     except Exception as e:
#         print(f"An error occurred: {e}")