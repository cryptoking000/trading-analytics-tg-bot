from database_function import db
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

async def Add_User_Start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    username = update.message.from_user.username
    connection_string = 'sqlitecloud://cqxv3cfvhz.sqlite.cloud:8860/telegram-database1?apikey=LatG9mr0j4cxwXHUjj9713u08qd5NmKtXfynbbabZP0'
    db.__init__(connection_string)

    # Check if user already exists
    existing_user = db.get_user(chat_id)
    if existing_user:
        await update.message.reply_text(f'Welcome back {username}!')
        return

    # Add new user to database with registration date
    last_active = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Set last_active to registration time
    success = db.add_user(
        chat_id=chat_id,
        username=username,
        expired_time=None,
        paid=False,
        transaction_key=None,
        last_active=last_active
    )

    if success:
        await update.message.reply_text(f'Welcome {username}! You have been registered.')
    else:
        await update.message.reply_text('Sorry, there was an error registering you.')