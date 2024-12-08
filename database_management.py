from database_function import db
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta



async def add_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    username = update.message.from_user.username
    
    # Check if user has both username and chat_id registered
    existing_user = db.get_user(chat_id)
    if existing_user and existing_user["username"] == username and username is not None:
        return

    # Add/Update user in database with registration date
    last_active = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    success = db.add_user(
        chat_id=chat_id,
        username=username,
        expired_time=None,
        paid=False,
        transaction_hash=None,
        last_active=last_active
    )

    if success:
        await update.message.reply_text(f'Welcome {username}! You have been registered.')
    else:
        await update.message.reply_text('Sorry, there was an error registering you.')

async def update_user_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    transaction_hash = f"tx_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    expired_time = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    
    # First check if user exists
    existing_user = db.get_user(chat_id)
    if not existing_user:
        await update.message.reply_text('Please register first using /start command.')
        return
        
    success = db.update_user_payment(
        chat_id=chat_id,
        paid=True,
        transaction_hash=transaction_hash,
        expired_time=expired_time
    )
    
    if success:
        await update.message.reply_text(f'Payment processed successfully! Your premium access is valid until {expired_time}')
    else:
        await update.message.reply_text('Sorry, there was an error processing your payment.')