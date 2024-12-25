from telethon.sync import TelegramClient
from datetime import datetime, timedelta
from pymongo import MongoClient
import requests
import json
import telethon.errors.rpcerrorlist
import time
import os
from dotenv import load_dotenv
import asyncio
load_dotenv()

# Load environment variables
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
phone_number = os.getenv("phone_number")
session_name = 'telegram_messages_session'
mongo_uri = os.getenv("MONGO_URI")

# Initialize MongoDB connection
mongo_client = MongoClient(mongo_uri)
db = mongo_client["telegram_bot_db"]
token_collection = db["token_contracts_analytics_data"]

# Load channel list
with open('channel.json', 'r') as file:
    channel_data = json.load(file)
    channel_list = channel_data['channels']

# Global variables
mention_flag = 0
message_count = 0
channel_count = 0
days_to_search = 15
offset_date = datetime.now() - timedelta(days=days_to_search)
start_number = 0  # Starting index for channel processing

def extract_token_contracts(message_text):
    """Extract token contract address from message text."""
    if not message_text:
        return None
        
    for part in message_text.split():
        if len(part) >= 40 and part.isalnum():
            return part
    return None

def get_token_contract_data(token_contracts):
    """Fetch and process token contract data from DexScreener API."""
    try:
        api_url = f"https://api.dexscreener.com/latest/dex/search?q={token_contracts}"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        pair_info = data.get('pairs', [])
        if not pair_info:
            print("No pairs found for the provided token contracts.")
            return None
            
        pair_data = pair_info[0]
        print("💚Successfully retrieved pair data")
        
        def safe_get(obj, *keys, default="N/A"):
            """Safely retrieve nested dictionary values."""
            try:
                current = obj
                for key in keys:
                    current = current[key]
                return current if current is not None else default
            except (KeyError, TypeError):
                print(f"Failed to get value for keys {keys}")
                return default

        # Extract token data
        token_data = {
            "token_address": token_contracts,
            "base_token_address": safe_get(pair_data, "baseToken", "address"),
            "base_token_symbol": safe_get(pair_data, "baseToken", "symbol"),
            "analytics_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "dex_url": safe_get(pair_data, "url"),
            "chain": safe_get(pair_data, "chainId"),
            "dex_id": safe_get(pair_data, "dexId"),
            "quote_token_symbol": safe_get(pair_data, "quoteToken", "symbol"),
            "token_price_usd": safe_get(pair_data, "priceUsd"),
            "liquidity_usd": safe_get(pair_data, "liquidity", "usd"),
            "volume_h24": safe_get(pair_data, "volume", "h24"),
            "price_change_h24": safe_get(pair_data, "priceChange", "h24"),
            "price_change_h1": safe_get(pair_data, "priceChange", "h1"),   
            "txns_buys_h24": safe_get(pair_data, "txns", "h24", "buys"),
            "txns_sells_h24": safe_get(pair_data, "txns", "h24", "sells"),
             "pairCreatedAt": safe_get(pair_data, "pairCreatedAt"),
            "origin_url": next((website.get("url") for website in safe_get(pair_data, "info", "websites", default=[]) 
                              if website.get("label") == "Website"), "#"),
            "telegram_url": next((social.get("url") for social in safe_get(pair_data, "info", "socials", default=[])
                                if social.get("type") == "telegram"), "#"),
            "twitter_url": next((social.get("url") for social in safe_get(pair_data, "info", "socials", default=[])
                               if social.get("type") == "twitter"), "#")
        }
        return token_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching token data: {e}")
        return None
async def all_day_mention_initialization():
    """Initialize mention data for all days."""
    try:
        print("🎈initializing....")
        for token_doc in token_collection.find():
            token_contracts = token_doc.get("token_contracts")
            token_contract_data = get_token_contract_data(token_contracts)
            token_collection.update_one(
                {"_id": token_doc["_id"]},
                {
                    "$set": {"daily_mentions": 0},
                    "$push": {"token_analytics_data": token_contract_data if token_contract_data else ""}
                }
            )
        print("🎈initialization complete")
    except Exception as e:
        print(f"Error resetting day mentions: {e}")
def message_collection(message):
    """Process and store message data containing token contracts."""
    global message_count
    global mention_flag
    token_contracts = extract_token_contracts(message.text)
    if not token_contracts:
        return False
        
    message_count += 1
    print("🎁", message_count, message.date, "🎈", token_contracts)
    
    message_dict = {
        "token_contracts": token_contracts,
        "mentioned_lastdate": message.date,
    }
    token_contract_data = get_token_contract_data(token_contracts)
    if not token_contract_data:
        pass

    existing_entry = token_collection.find_one({"token_contracts": {"$in": [message_dict["token_contracts"]]}})

    if not existing_entry:
        # Insert new entry
        token_collection.insert_one({
            **message_dict,
            "total_mentions": 1,
            "mentioned_lastdate": message.date,
            "daily_mentions": 1,
            "token_analytics_data": [token_contract_data] if token_contract_data else [""],
        })
        print("🧨 New token entry created")
    # elif existing_entry["mentioned_lastdate"].strftime("%Y-%m-%d %H:%M:%S") != message.date.strftime("%Y-%m-%d %H:%M:%S"):
        # Update existing entry
    else:
        print("🧨🧨 Updating existing entry")

        # Update base fields
        token_collection.update_one(
            {"_id": existing_entry["_id"]},
            {"$set": {
                "total_mentions": existing_entry["total_mentions"] + 1,
                "mentioned_lastdate": message.date,
                "daily_mentions": existing_entry["daily_mentions"] + 1
            }}
        )       
        # if mention_flag == 0:#run once a day(main)
            # Check if arrays exceed max size and update accordingly
        if len(existing_entry.get("token_analytics_data", [])) > 3:
            print("🧨🧨🧨🧨🧨poped")
            token_collection.update_one(
                {"_id": existing_entry["_id"]},
                {
                    "$pop": {
                        "token_analytics_data": -1
                    }
                }
            )
            # Update historical data arrays
            
            
    mention_flag = 1
    return True

async def main():
    """Main function to process messages from Telegram channels."""    
    global channel_count
    global mention_flag 
    mention_flag = 0
    
    await all_day_mention_initialization()
        
    async with TelegramClient(session_name, TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        for channel_username in channel_list[start_number:]:
            channel_count += 1
            print("🎁🎁🎁🎁", channel_count, "/", len(channel_list), channel_username)
            
            try:
                has_token = False
                async for message in client.iter_messages(channel_username):
                    if message.date.date() >= offset_date.date():
                        if message_collection(message):
                            has_token = True
                    else:
                        break
                
                if not has_token:
                    with open('channel.json', 'r+') as file:
                        channel_data = json.load(file)
                        if channel_username in channel_data['channels']:
                            channel_data['channels'].remove(channel_username)
                            print(f"remove❌: {channel_username}")
                            file.seek(0)
                            json.dump(channel_data, file, indent=4)
                            file.truncate()
                        
            except telethon.errors.rpcerrorlist.FloodWaitError as e:
                print(f'Rate limit exceeded. Sleeping for {e.seconds} seconds')
                await asyncio.sleep(e.seconds)
                
            except telethon.errors.rpcerrorlist.ChannelPrivateError:
                print(f"Access denied to channel: {channel_username}")
                with open('channel.json', 'r+') as file:
                    channel_data = json.load(file)
                    if channel_username in channel_data['channels']:
                        channel_data['channels'].remove(channel_username)
                        print(f"remove❌private channel-: {channel_username}")
                        file.seek(0)
                        json.dump(channel_data, file, indent=4)
                        file.truncate()
                
            except Exception as e:
                print(f"Error processing channel {channel_username}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    print("🎁 Offset date:", offset_date)
    print("🎁 Finished at:", datetime.now())