from telethon.sync import TelegramClient
from pymongo import MongoClient
from datetime import datetime
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
import json
from telethon.errors import SessionPasswordNeededError
from getpass import getpass
from datetime import datetime, timedelta

TELEGRAM_API_ID = '20774786'
TELEGRAM_API_HASH = '9d57e018be785b18b245632f508302f2'
phone_number = '+17344305801'  # Fixed: Added quotes to make it a string
import os

session_name = 'telegram_messages_session9'


# Load channel list from JSON file
with open('channel.json', 'r') as file:
    channel_data = json.load(file)
    channel_list = channel_data['channels']

limit = 100

# MongoDB connection
mongo_uri = "mongodb+srv://andyblake:crs19981106@messagescluster.ci599.mongodb.net/?retryWrites=true&w=majority&appName=MessagesCluster"
mongo_client = MongoClient(mongo_uri)
db = mongo_client["telegram_bot_db"]
messages_collection = db["messages"]
async def tlg_connect(api_id, api_hash, phone_number):
    '''Connect and Log-in/Sign-in to Telegram API. Request Sign-in code for first execution'''
    try:
        print('Connecting to Telegram...')
        client = TelegramClient(session_name, api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            print('Session file not found. Initiating first-time authentication...')
            await client.send_code_request(phone_number)
            
            while True:
                try:
                    code = input('Enter the verification code received: ')
                    await client.sign_in(phone_number, code)
                    break
                except SessionPasswordNeededError:
                    password = getpass('Two-factor authentication enabled. Enter your password: ')
                    await client.sign_in(password=password)
                    break
                except Exception as e:
                    print(f'Authentication failed: {str(e)}')
                    continue

        print('Successfully authenticated with Telegram')
        return client

    except Exception as e:
        print(f'Failed to connect to Telegram: {str(e)}')
        return None

async def collect_messages(client, chat_name, limit):
    try:
        # Get chat info 
        chat_info = await client.get_entity(chat_name)
        
        offset_date = datetime.now() - timedelta(days=7)  # Fetch messages from a week ago
        messages = await client.get_messages(chat_info, limit=limit, offset_date=offset_date)

        print(messages)
        # return the results in a dictionary
        return {"messages": messages, "channel": chat_info}
    except Exception as e:
        print(f"Error collecting messages: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    print("Starting message collection...")
    client = None
    try:
        client = await tlg_connect(TELEGRAM_API_ID, TELEGRAM_API_HASH, phone_number)
        if not client:
            await update.message.reply_text("Failed to connect to Telegram")
            return

        for channel in channel_list:
            try:
                chat_name = channel
                message_data = await collect_messages(client, chat_name, limit)
                if not message_data:
                    print(f"No data collected for channel: {chat_name}")
                    continue

                # Convert messages to a format that can be serialized to MongoDB
                messages_list = []
                for msg in message_data["messages"]:
                    # Get sender information safely
                    sender = await msg.get_sender()
                    username = sender.username if sender else None
                    
                    message_dict = {
                        "sender_username": username,
                        "sender_id": sender.id if sender else None,
                        "date": msg.date,
                        "message": msg.text if msg.text else None,  # Use text instead of message
                        "message_id": msg.id
                    }
                    messages_list.append(message_dict)
            
                # Create a single JSON document containing all messages
                json_document = {
                    "channel_name": message_data["channel"].username,
                    "last_updated": str(datetime.now()),
                    "messages": messages_list
                }
            
                # Insert the JSON document into MongoDB
                messages_collection.insert_one(json_document)
                await update.message.reply_text(f"{chat_name} 😆Messages saved to MongoDB as JSON document")
            except Exception as channel_error:
                print(f"Error processing channel {chat_name}: {channel_error}")
                continue
        
        await update.message.reply_text("All messages saved to MongoDB as JSON document")
    except Exception as e:
        print(f"Error in start command: {e}")
        await update.message.reply_text("An error occurred while collecting messages")
    finally:
        if client:
            try:
                await client.disconnect()
            except Exception as disconnect_error:
                print(f"Error disconnecting client: {disconnect_error}")

# Modify the main block to include proper shutdown handling
if __name__ == "__main__":
    app = ApplicationBuilder().token("7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4").build()
    
    # Add error handler
    async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(f"Exception while handling an update: {context.error}")
    
    app.add_error_handler(error_handler)
    
    try:
        mongo_client.admin.command('ping')
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        exit(1)
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is running...")
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except KeyboardInterrupt:
        print("\nBot stopped gracefully")
    except Exception as e:
        print(f"Error running bot: {e}")
    finally:
        app.stop()
        mongo_client.close()