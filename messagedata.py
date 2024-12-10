from telethon.sync import TelegramClient
from pymongo import MongoClient
from datetime import datetime
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
channel_list = ["dexscreenerchat", "GeNeSiS_Lounge"]

# Telegram API credentials
api_id = '20774786'
api_hash = '9d57e018be785b18b245632f508302f2'
session_name = 'telegram_messages_session'
bot_token = '7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4'

# MongoDB connection
mongo_uri = "mongodb+srv://andyblake:crs19981106@messagescluster.ci599.mongodb.net/?retryWrites=true&w=majority&appName=MessagesCluster"
mongo_client = MongoClient(mongo_uri)
db = mongo_client["telegram_bot_db"]
messages_collection = db["messages"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    try:
        async with TelegramClient(session_name, api_id, api_hash) as client:
            await client.start()
            
            # Iterate through each channel
            for channel_username in channel_list:
                try:
                    # Get messages from channel
                    async for message in client.iter_messages(channel_username, limit=100):
                        # Create message document
                        message_doc = {
                            "message_id": message.id,
                            "channel": channel_username,
                            "text": message.text if message.text else "",
                            "date": message.date,
                            "from_id": message.from_id.user_id if message.from_id else None,
                            "reply_to_msg_id": message.reply_to_msg_id,
                            "forward_from": message.forward.from_id if message.forward else None,
                            "created_at": datetime.now()
                        }
                        
                        # Insert into MongoDB
                        try:
                            messages_collection.insert_one(message_doc)
                        except Exception as e:
                            print(f"Error saving message {message.id} from {channel_username}: {str(e)}")
                except Exception as e:
                    print(f"Error accessing channel {channel_username}: {str(e)}")
                    continue
    except Exception as e:
        print(f"Error in main client connection: {str(e)}")

# if __name__ == "__main__":
#     import asyncio

#     # Check MongoDB connection
#     try:
#         mongo_client.admin.command('ping')
#         print("Successfully connected to MongoDB")
#     except Exception as e:
#         print(f"Error connecting to MongoDB: {e}")
#         exit(1)
        
#     print("Starting message collection...")
#     asyncio.run(save_messages())

if __name__ == "__main__":
    app = ApplicationBuilder().token("7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4").build()
    try:
        mongo_client.admin.command('ping')
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        exit(1)
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    # app.add_handler(CommandHandler("users", show_users))

    print("Bot is running...")
    app.run_polling()