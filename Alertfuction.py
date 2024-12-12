from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters, CommandHandler
from database_function import db
from apidata import fetch_trading_pair_data

import asyncio

async def add_to_watchlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    # Extract token data from callback data
    _, chain_id, token_address = query.data.split(":")

    # Add to database watchlist
    success = db.add_to_watchlist(user_id, chain_id, token_address)
    
    if success:
        await query.answer("Token added to your watchlist!")
    else:
        await query.answer("Token is already in your watchlist!")

    # Remove keyboard to avoid re-clicks
    await query.edit_message_reply_markup(reply_markup=None)

async def set_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    # Extract token data from callback data  
    _, chain_id, token_address = query.data.split(":")

    # Default alert condition
    alert_condition = {"type": "price_above", "value": 0.0001}

    # Add alert to database
    success = db.add_alert(user_id, chain_id, token_address, alert_condition)

    if success:
        await query.answer("Alert has been set!")
    else:
        await query.answer("Failed to set alert")
    
    await query.edit_message_reply_markup(reply_markup=None)

async def set_alert_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chain_id, token_address = query.data.split(":")[1:]
    context.user_data["token_chain_id"] = chain_id
    context.user_data["token_address"] = token_address

    # Ask user for condition
    keyboard = [
        [
            InlineKeyboardButton("Goes over", callback_data="alert_condition:over"),
            InlineKeyboardButton("Goes under", callback_data="alert_condition:under"),
        ]
    ]
    await query.message.reply_text(
        "🔔 Choose an alert condition:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def check_alerts(context: ContextTypes.DEFAULT_TYPE) -> None:
    bot = context.bot
    while True:
        try:
            alerts = db.get_active_alerts()
            
            for alert in alerts:
                user_id = alert["user_id"]
                chain_id = alert["chain_id"] 
                token_address = alert["token_address"]
                condition = alert["condition"]

                data, _ = await fetch_trading_pair_data(token_address, user_id)
                if data:
                    price_line = [line for line in data.split('\n') if "💰 USD:" in line][0]
                    current_price = float(price_line.split('$')[1].strip('`'))

                    if (condition["type"] == "price_above" and current_price > condition["value"]) or \
                       (condition["type"] == "price_under" and current_price < condition["value"]):
                        await bot.send_message(
                            chat_id=user_id,
                            text=f'🔔 Alert: Token price is now ${current_price}!'
                        )
                        db.mark_alert_triggered(alert["id"])

        except Exception as e:
            print(f"Error checking alerts: {e}")
            
        await asyncio.sleep(60)

async def handle_alert_condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    condition = query.data.split(":")[1]
    context.user_data["alert_condition"] = condition

    # Prompt user for price input
    await query.message.reply_text(
        "💲 Enter the price threshold (e.g., 0.0003994):"
    )

async def handle_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = float(update.message.text)
        chain_id = context.user_data.get("token_chain_id")
        token_address = context.user_data.get("token_address")
        condition_type = context.user_data.get("alert_condition")

        if not all([chain_id, token_address, condition_type]):
            await update.message.reply_text("⚠️ Missing alert information. Please start over.")
            return

        # Create alert condition
        alert_condition = {
            "type": f"price_{condition_type}",
            "value": price
        }

        # Save alert to database
        user_id = update.message.from_user.id
        success = db.add_alert(user_id, chain_id, token_address, alert_condition)

        if success:
            await update.message.reply_text(
                f"🔔 Alert set: Will notify when price goes {condition_type} ${price} USD!"
            )
        else:
            await update.message.reply_text("⚠️ Failed to set alert. Please try again.")

    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid price.")

def setup_handlers(application):
    application.add_handler(CallbackQueryHandler(set_alert_handler, pattern="^set_alert"))
    application.add_handler(CallbackQueryHandler(handle_alert_condition, pattern="^alert_condition"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_price_input))
    
    # Start alert monitoring
    application.job_queue.run_repeating(check_alerts, interval=60)
