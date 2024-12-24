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
message_count = 0
channel_count = 0
days_to_search = 10
offset_date = datetime.now() - timedelta(days=days_to_search)
start_number = 1  # Starting index for channel processing

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
        print("Successfully retrieved pair data")
        
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
            "token_contracts": token_contracts,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "chain": safe_get(pair_data, "chainId"),
            "dex_id": safe_get(pair_data, "dexId"),
            "pairAddress": safe_get(pair_data, "pairAddress"),
            "base_token_address": safe_get(pair_data, "baseToken", "address"),
            "quote_token_address": safe_get(pair_data, "quoteToken", "address"),
            "base_token_name": safe_get(pair_data, "baseToken", "name", default="Unknown"),
            "quote_token_name": safe_get(pair_data, "quoteToken", "name", default="Unknown"),
            "base_token_symbol": safe_get(pair_data, "baseToken", "symbol"),
            "quote_token_symbol": safe_get(pair_data, "quoteToken", "symbol"),
            "price_native": safe_get(pair_data, "priceNative"),
            "price_usd": safe_get(pair_data, "priceUsd"),
            "fdv": safe_get(pair_data, "fdv"),
            "liquidity": {
                "usd": safe_get(pair_data, "liquidity", "usd"),
                "base": safe_get(pair_data, "liquidity", "base"),
                "quote": safe_get(pair_data, "liquidity", "quote")
            },
            "volume": {
                "h24": safe_get(pair_data, "volume", "h24"),
                "h6": safe_get(pair_data, "volume", "h6"),
                "h1": safe_get(pair_data, "volume", "h1"),
                "m5": safe_get(pair_data, "volume", "m5")
            },
            "price_change": {
                "h1": safe_get(pair_data, "priceChange", "h1"),
                "h24": safe_get(pair_data, "priceChange", "h24"),
                "h6": safe_get(pair_data, "priceChange", "h6"),
                "m5": safe_get(pair_data, "priceChange", "m5")
            },
            "txns": {
                "buys": {
                    "h1": safe_get(pair_data, "txns", "h1", "buys"),
                    "h24": safe_get(pair_data, "txns", "h24", "buys"),
                    "h6": safe_get(pair_data, "txns", "h6", "buys"),
                    "m5": safe_get(pair_data, "txns", "m5", "buys")
                },
                "sells": {
                    "h1": safe_get(pair_data, "txns", "h1", "sells"),
                    "h24": safe_get(pair_data, "txns", "h24", "sells"),
                    "h6": safe_get(pair_data, "txns", "h6", "sells"),
                    "m5": safe_get(pair_data, "txns", "m5", "sells")
                }
            },
            "token_age": safe_get(pair_data, "pairCreatedAt"),
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

def message_collection(message):
    """Process and store message data containing token contracts."""
    global message_count
    
    token_contracts = extract_token_contracts(message.text)
    if not token_contracts:
        return
        
    message_count += 1
    print("🎁", message_count, message.date, "🎈", token_contracts)
    
    message_dict = {
        "token_contracts": token_contracts,
        "last_mention_date": message.date,
    }
    token_contract_data = get_token_contract_data(token_contracts)
    if not token_contract_data:
        return

    existing_entry = token_collection.find_one({"token_contracts": {"$in": [message_dict["token_contracts"]]}})

    if not existing_entry:
        # Insert new entry
        token_collection.insert_one({
            **message_dict,
            "num_times_all_mentioned": 1,
            "last_mention_date": message.date,
            "all_token_data": {
                "mentioned_message_dates": [message.date],
                "num_times_mentioned": [1],
                "token_analytics_data": [token_contract_data],
            }
        })
        print("🧨 New token entry created")
    elif existing_entry["last_mention_date"].strftime("%Y-%m-%d %H:%M:%S") != message.date.strftime("%Y-%m-%d %H:%M:%S"):
        # Update existing entry
        print("🧨🧨 Updating existing entry")

        # Update base fields
        token_collection.update_one(
            {"_id": existing_entry["_id"]},
            {"$set": {
                "num_times_all_mentioned": existing_entry["num_times_all_mentioned"] + 1,
                "last_mention_date": message.date,
            }}
        )

        # Update historical data arrays
        token_collection.update_one(
            {"_id": existing_entry["_id"]},
            {"$push": {
                "all_token_data.mentioned_message_dates": message.date,
                "all_token_data.num_times_mentioned": existing_entry["all_token_data"]["num_times_mentioned"][-1] + 1,
                "all_token_data.token_analytics_data": token_contract_data
            }}
        )
        print("Successfully updated token data")

async def main():
    """Main function to process messages from Telegram channels."""    
    global channel_count

    async with TelegramClient(session_name, TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
        for channel_username in channel_list[start_number:]:
            channel_count += 1
            print("🎁🎁🎁🎁", channel_count, "/", len(channel_list), channel_username)
            
            try:
                async for message in client.iter_messages(channel_username):
                    if message.date.date() >= offset_date.date():
                        message_collection(message)
                    else:
                        break
                        
            except telethon.errors.rpcerrorlist.FloodWaitError as e:
                print(f'Rate limit exceeded. Sleeping for {e.seconds} seconds')
                time.sleep(e.seconds)
                
            except telethon.errors.rpcerrorlist.ChannelPrivateError:
                print(f"Access denied to channel: {channel_username}")
                # Remove private channel from list
                with open('channel.json', 'r+') as file:
                    channel_data = json.load(file)
                    if channel_username in channel_data['channels']:
                        channel_data['channels'].remove(channel_username)
                        file.seek(0)
                        json.dump(channel_data, file, indent=4)
                        file.truncate()
                        
            except Exception as e:
                print(f"Error processing channel {channel_username}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    print("🎁 Offset date:", offset_date)
    print("🎁 Finished at:", datetime.now())
