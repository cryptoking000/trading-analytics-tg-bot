from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from math_function import convert_usd_to_crypto

# Module for keyboard layouts
def get_duration_keyboard():
    return [
        [
            InlineKeyboardButton("1 Month ($50)", callback_data="duration:1:50"),
            InlineKeyboardButton("3 Months ($120)", callback_data="duration:3:120")
        ],
        [InlineKeyboardButton("1 Year ($500)", callback_data="duration:12:500")]
    ]

def get_payment_keyboard():
    return [
        [
            InlineKeyboardButton("BSC", callback_data="pay:BSC"),
            InlineKeyboardButton("ETH", callback_data="pay:ETH"), 
            InlineKeyboardButton("SOL", callback_data="pay:SOL")
        ],
        [InlineKeyboardButton("Back", callback_data="back")]
    ]

# Module for subscription start
async def payment_start(update: Update, context):
    keyboard = get_duration_keyboard()
    message = "Select your subscription duration:"
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)

# Module for handling button interactions
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    # Store current state if not a back button
    if not query.data == "back":
        if "state_history" not in context.user_data:
            context.user_data["state_history"] = []
        current_state = {
            "message": query.message.text,
            "keyboard": query.message.reply_markup.inline_keyboard
        }
        context.user_data["state_history"].append(current_state)
    
    # Handle duration selection
    if query.data.startswith("duration:"):
        duration, price = query.data.split(":")[1:]
        context.user_data["duration"] = int(duration)
        context.user_data["price"] = float(price)
        
        keyboard = get_payment_keyboard()
        message = "Select payment method:"
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)

    # Handle payment method selection
    elif query.data.startswith("pay:"):
        chain = query.data.split(":")[1]
        price_usd = context.user_data.get("price", 0)  # Use get() with default value
        
        wallet_addresses = {
            "BSC": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "ETH": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 
            "SOL": "8njqnN9ZRQkvUFPNzjEU1mXMfPrC54zugmUeZoAYR659"
        }

        # Convert USD to crypto amounts
        crypto_amounts = convert_usd_to_crypto(price_usd)
        # print(crypto_amounts)
        message = (
            f"Please send {crypto_amounts[chain]} {chain} (${price_usd}) to the following address to confirm your subscription.\n\n"
            f"`{wallet_addresses[chain]}`\n\n"
            "Once you paid, please send the transaction hash."
        )
        
        keyboard = [[InlineKeyboardButton("Back", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

    # Handle back button - returns to previous state
    elif query.data == "back":
        if "state_history" in context.user_data and context.user_data["state_history"]:
            # Get previous state
            previous_state = context.user_data["state_history"].pop()
            message = previous_state["message"]
            keyboard = previous_state["keyboard"]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=message, reply_markup=reply_markup)
        else:
            # If no history, go back to duration selection
            keyboard = get_duration_keyboard()
            message = "Select your subscription duration:"
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=message, reply_markup=reply_markup)
            context.user_data.clear()
