import sqlitecloud
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Connection string for SQLite Cloud
DB_CONNECTION_STRING = 'sqlitecloud://cqxv3cfvhz.sqlite.cloud:8860/telegram-database1?apikey=LatG9mr0j4cxwXHUjj9713u08qd5NmKtXfynbbabZP0'

class DBHelper:
    def __init__(self):
        # Connect to the SQLite Cloud database
        self.conn = sqlitecloud.connect(DB_CONNECTION_STRING)
        # self.conn.execute('abc')
        self.setup()

    def setup(self):
        print("🎈Creating table")
        
        stmt = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER UNIQUE,
            username TEXT,
            expired_time TIMESTAMP,
            paid BOOLEAN DEFAULT 0,
            transaction_key TEXT
        )
        '''
        self.conn.execute(stmt)
        self.conn.commit()

    def add_user(self, chat_id, username, expired_time, paid, transaction_key):
        stmt = '''
        INSERT INTO users (chat_id, username, expired_time, paid, transaction_key) 
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(chat_id) DO UPDATE SET 
            username=excluded.username,
            expired_time=excluded.expired_time,
            paid=excluded.paid,
            transaction_key=excluded.transaction_key;
        '''
        args = (chat_id, username, expired_time, paid, transaction_key)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_user(self, chat_id):
        stmt = "DELETE FROM users WHERE chat_id = ?"
        args = (chat_id,)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def update_user(self, chat_id, username=None, expired_time=None, paid=None, transaction_key=None):
        updates = []
        args = []

        if username is not None:
            updates.append("username = ?")
            args.append(username)
        
        if expired_time is not None:
            updates.append("expired_time = ?")
            args.append(expired_time)

        if paid is not None:
            updates.append("paid = ?")
            args.append(paid)

        if transaction_key is not None:
            updates.append("transaction_key = ?")
            args.append(transaction_key)

        if updates:
            stmt = f"UPDATE users SET {', '.join(updates)} WHERE chat_id = ?"
            args.append(chat_id)
            self.conn.execute(stmt, args)
            self.conn.commit()

    def get_user(self, chat_id, special_data):
        stmt = f"SELECT `{special_data}` FROM users WHERE chat_id = ?"
        args = (chat_id,)
        cursor = self.conn.execute(stmt, args)
        return cursor.fetchone()  # Returns a single user record

# Telegram Bot Functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Welcome! Please provide your username.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat.id
    username = update.message.text.strip()  # Get the username from the message

    # For demonstration purposes: set some default values
    expired_time = None  # Set this to a valid timestamp if needed
    paid = False         # Default value for 'paid'
    transaction_key = None  # Set this to a valid key if needed

    db_helper.add_user(chat_id, username, expired_time, paid, transaction_key)
    
    await update.message.reply_text(f"User '{username}' with chat ID {chat_id} saved successfully!")

def main():
    global db_helper
    db_helper = DBHelper()  # Initialize the database helper
    
    application = ApplicationBuilder().token("7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4").build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == '__main__':
    main()