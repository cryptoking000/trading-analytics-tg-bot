from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup

async def payment_start(update: Update, context):
    # Define keyboard layout for subscription durations
    keyboard = [
        [
            InlineKeyboardButton("1 Month ($50)", callback_data="duration:1:50"),
            InlineKeyboardButton("3 Months ($120)", callback_data="duration:3:120")
        ],
        [InlineKeyboardButton("1 Year ($500)", callback_data="duration:12:500")]
    ]
    message = "Select your subscription duration:"
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)

# Handle subscription selection
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("duration:"):
        # Store duration and price in context
        duration, price = query.data.split(":")[1:]
        context.user_data["duration"] = int(duration)
        context.user_data["price"] = float(price)
        
        # After duration selection, show payment methods
        keyboard = [
            [
                InlineKeyboardButton("BSC", callback_data="pay:BSC"),
                InlineKeyboardButton("ETH", callback_data="pay:ETH"), 
                InlineKeyboardButton("SOL", callback_data="pay:SOL")
            ],
            [InlineKeyboardButton("Back", callback_data="back")]
        ]
        message = "Select payment method:"
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)

    elif query.data.startswith("pay:"):
        chain = query.data.split(":")[1]
        price = context.user_data["price"]
        months = context.user_data["duration"]
        
        # Wallet addresses for each chain
        wallet_addresses = {
            "BSC": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "ETH": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 
            "SOL": "8njqnN9ZRQkvUFPNzjEU1mXMfPrC54zugmUeZoAYR659"
        }
        
        message = (
            f"Please send {price} {chain} to the following address to confirm your subscription.\n\n"
            f"`{wallet_addresses[chain]}`\n\n"
            "Once you paid, please send the transaction hash."
        )
        
        await query.edit_message_text(
            text=message,
            parse_mode='Markdown'
        )

    elif query.data == "back":
        # Call payment_start with the required parameters
        await payment_start(update, context)