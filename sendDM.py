import asyncio
import telegram
import requests
import json
from database_function import db
import os
from dotenv import load_dotenv
from ai_insight import ai_insight
from pymongo import MongoClient
from datetime import datetime
from messagecollection import get_token_contract_data
load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri)
db = mongo_client["telegram_bot_db"]
token_collection = db["token_contracts"]
TOKEN = os.getenv("bot_token")
 # Default chat_id if no recent messages

URL_TELEGRAM_BASE = f'https://api.telegram.org/bot{TOKEN}'
URL_GET_UPDATES = f'{URL_TELEGRAM_BASE}/getUpdates'

# Flag to control the DM service
dm_task = None

async def send_message(text, chat_id):
    try:
        # Create a new bot instance for each message
        temp_bot = telegram.Bot(token=TOKEN)
        # Send async message using the temporary bot
        await temp_bot.send_message(chat_id=chat_id, text=text)
        return True
    except telegram.error.TelegramError as e:
        print(f"Failed to send message to {chat_id}: {str(e)}")
        return False

async def send_dm():
    try:
        # Get all users from database
        users = db.get_all_users()
        processed_chat_ids = set()

        if not users:
            print("No users found in database.")
            return

        for user in users:
            chat_id = user.get('chat_id')
            if not chat_id:
                print(f"Invalid chat_id for user: {user}")
                continue
                
            is_paid = user.get('is_paid', False)
            username = user.get('username', 'User')
            ai_insight_text = await ai_insight()
            if chat_id not in processed_chat_ids:
                message = (
                    f"Hello {username}!\n\n"
                    f"{' Thank you for being our premium member!' if is_paid else '💫 Upgrade to premium for more features!'}\n"
                    f"{f'{ai_insight_text}' if is_paid else ''}"
                    f"Use /help to see available commands."
                )
                
                if await send_message(text=message, chat_id=chat_id):
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
        dm_task = None
    print("DM service stopped successfully")
async def all_token_data_update():
    for token_contract in token_collection.find():
        await token_data_update(token_contract)
async def token_data_update(token_contract):
    token_contract_data = get_token_contract_data(token_contract["token_contracts"])
    existing_entry = token_collection.find_one({"token_contracts": {"$in": [token_contract["token_contracts"]]}})
    order_token_contract_data = datetime.now().hour
    token_collection.update_one(
            {"_id": existing_entry["_id"]},
            {"$set": {
                "all_data": {
                    **existing_entry["all_data"],  # Preserve previous data
                    f"message_date({order_token_contract_data})": datetime.now(),
                    f"num_times_mentioned({order_token_contract_data})": existing_entry["num_times_mentioned"],  
                    f"token_contract_data({order_token_contract_data})": token_contract_data,
                }
            }}
        )
    print("Successfully updated token data")

async def periodic_dm():
    try:
        print("Token data updating...")
        await all_token_data_update()
        print("Token data updated")
        await asyncio.sleep(10)
        print("DM service starting...")
        await send_dm()
        await asyncio.sleep(200)  # Wait for 20 seconds before next execution
        asyncio.create_task(periodic_dm())  # Schedule next execution
    except asyncio.CancelledError:
        print("DM service cancelled")
    except Exception as e:
        print(f"Error in DM service: {str(e)}")
        await asyncio.sleep(50)  # Short sleep on error
        asyncio.create_task(periodic_dm())  # Retry on error

async def start_dm_service():
    global dm_task
    print("DM service starting...")
    dm_task = asyncio.create_task(periodic_dm())
