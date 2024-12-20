from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["telegram_bot_db"]
users_collection = db["users"]
bot_token = os.getenv("bot_token")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    chat_id = update.effective_chat.id
    first_name = update.effective_chat.first_name
    username =update.effective_chat.username

    # Check if user already exists in the database
    user = users_collection.find_one({"chat_id": chat_id})
    if user:
        message = f"Welcome back, {first_name}!"
    else:
        # Save new user to the database
        users_collection.insert_one({
            "chat_id": chat_id,
            "first_name": first_name,
            "username": username,
            "joined": update.effective_message.date
        })
        message = f"Hello, {first_name}! You are now registered."
    
    await context.bot.send_message(chat_id=chat_id, text=message)

async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle a command to show all registered users."""
    all_users = users_collection.find()
    message = "👥 Registered Users:\n"
    async for user in all_users:
        message += f"- {user['first_name']} (ID: {user['chat_id']})\n"
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

if __name__ == "__main__":
    app = ApplicationBuilder().token(bot_token).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", show_users))

    print("Bot is running...")
    app.run_polling()
