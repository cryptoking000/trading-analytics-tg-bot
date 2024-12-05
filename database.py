from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import sqlitecloud
import asyncio

# Connection string for SQLite Cloud
DB_CONNECTION_STRING = 'sqlitecloud://cqxv3cfvhz.sqlite.cloud:8860/abc?apikey=LatG9mr0j4cxwXHUjj9713u08qd5NmKtXfynbbabZP0'

def create_database():
    try:
        # Connect to the SQLite Cloud database
        conn = sqlitecloud.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        # Explicitly select the database if required, typically looks like this:
        # cursor.execute('abc')

        # Create table for storing user chat IDs and token addresses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE,
                is_paid BOOLEAN,
                token_address TEXT
            )
        ''')
        print("Table created successfully")
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


def save_user_data(chat_id: int, token_address: str):
    try:
        conn = sqlitecloud.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO users (chat_id, token_address) VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET token_address=excluded.token_address;
        ''', (chat_id, token_address))
        
        conn.commit()
    except Exception as e:
        print(f"An error occurred while saving user data: {e}")
    finally:
        conn.close()


# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat.id
    save_user_data(chat_id,None)
    await update.message.reply_text(f"Welcome!your chat ID{chat_id} Please send your token address.")
    
    # Save initial user data (not paid by default)
    # save_user_data(chat_id)

# Handler for receiving text messages (token addresses)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat.id
    token_address = update.message.text.strip()  # Get the token address from the message
    
    # Save or update user data with the provided token address
    save_user_data(chat_id, token_address=token_address)
    
    await update.message.reply_text(f"Token address '{token_address}'chat ID {chat_id} saved successfully!")

def main():
    # create_database()  # Ensure the database is created before starting the bot
    
    application = ApplicationBuilder().token("7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4").build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()


if __name__ == '__main__':
  
    main()