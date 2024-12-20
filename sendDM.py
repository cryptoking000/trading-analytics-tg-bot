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
from typing import Optional

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri)
db = mongo_client["telegram_bot_db"]
token_collection = db["token_contracts"]
TOKEN = os.getenv("bot_token")

URL_TELEGRAM_BASE = f'https://api.telegram.org/bot{TOKEN}'
URL_GET_UPDATES = f'{URL_TELEGRAM_BASE}/getUpdates'

# Flag to control the DM service
dm_task: Optional[asyncio.Task] = None

async def send_message(text: str, chat_id: int) -> bool:
    """Send a message to a specific chat ID.
    
    Args:
        text: The message text to send
        chat_id: The recipient's chat ID
        
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        async with telegram.Bot(token=TOKEN) as bot:
            await bot.send_message(chat_id=chat_id, text=text)
            return True
    except telegram.error.TelegramError as e:
        print(f"Failed to send message to {chat_id}: {str(e)}")
        return False

async def send_dm() -> None:
    """Send DM messages to all users in database."""
    try:
        users = db.get_all_users()
        processed_chat_ids = set()

        if not users:
            print("No users found in database.")
            return

        ai_insight_text = await ai_insight()
        
        async def process_user(user):
            chat_id = user.get('chat_id')
            if not chat_id:
                print(f"Invalid chat_id for user: {user}")
                return
                
            if chat_id in processed_chat_ids:
                return
                
            is_paid = user.get('is_paid', False)
            username = user.get('username', 'User')
            
            message = (
                f"Hello {username}!\n\n"
                f"{' Thank you for being our premium member!' if is_paid else '💫 Upgrade to premium for more features!'}\n"
                f"{ai_insight_text if is_paid else ''}"
                f"Use /help to see available commands."
            )
            
            if await send_message(text=message, chat_id=chat_id):
                processed_chat_ids.add(chat_id)
                print(f"Successfully sent message to {username} (ID: {chat_id})")
            else:
                print(f"Failed to send message to {username} (ID: {chat_id})")
                
        await asyncio.gather(*[process_user(user) for user in users])
            
    except Exception as e:
        print(f"Error in send_dm: {str(e)}")

async def stop_dm_service() -> None:
    """Stop the DM service task."""
    global dm_task
    if dm_task and not dm_task.done():
        dm_task.cancel()
        try:
            await dm_task
        except asyncio.CancelledError:
            pass
        finally:
            dm_task = None
    print("DM service stopped successfully")

async def all_token_data_update() -> None:
    """Update all token contract data concurrently."""
    async def update_single_token(token_contract):
        try:
            return await token_data_update(token_contract)
        except Exception as e:
            print(f"Error updating token {token_contract}: {e}")
            return None
            
    token_contracts = [contract async for contract in token_collection.find()]
    await asyncio.gather(*[update_single_token(contract) for contract in token_contracts])

async def token_data_update(token_contract: dict) -> None:
    """Update data for a single token contract.
    
    Args:
        token_contract: Token contract document from database
    """
    try:
        token_contract_data = await asyncio.to_thread(
            get_token_contract_data,
            token_contract["token_contracts"]
        )
        
        existing_entry = await asyncio.to_thread(
            token_collection.find_one,
            {"token_contracts": {"$in": [token_contract["token_contracts"]]}}
        )
        
        if not existing_entry:
            return
            
        order_token_contract_data = datetime.now().hour
        
        await asyncio.to_thread(
            token_collection.update_one,
            {"_id": existing_entry["_id"]},
            {"$set": {
                "all_data": {
                    **existing_entry["all_data"],
                    f"message_date({order_token_contract_data})": datetime.now(),
                    f"num_times_mentioned({order_token_contract_data})": existing_entry["num_times_mentioned"],
                    f"token_contract_data({order_token_contract_data})": token_contract_data,
                }
            }}
        )
        print("Successfully updated token data")
    except Exception as e:
        print(f"Error updating token data: {str(e)}")
        raise

async def periodic_dm() -> None:
    """Periodically update token data and send DMs."""
    while True:
        try:
            print("Token data updating...")
            await all_token_data_update()
            print("Token data updated")
            
            await asyncio.sleep(10)
            
            print("DM service starting...")
            await send_dm()
            
            await asyncio.sleep(200)
            
        except asyncio.CancelledError:
            print("DM service cancelled")
            break
        except Exception as e:
            print(f"Error in DM service: {str(e)}")
            await asyncio.sleep(50)

async def start_dm_service() -> None:
    """Start the DM service task."""
    global dm_task
    if dm_task and not dm_task.done():
        print("DM service already running")
        return
        
    print("DM service starting...")
    dm_task = asyncio.create_task(periodic_dm())
