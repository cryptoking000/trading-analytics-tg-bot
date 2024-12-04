from telegram import Update, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup

async def payment_start(update: Update, context):
    # Define keyboard layout for subscription plans
    keyboard = [
        [InlineKeyboardButton("1 Month: $4.99", callback_data="plan_1month")],
        [InlineKeyboardButton("1 Year: $49.99", callback_data="plan_1year")],
        [InlineKeyboardButton("Lifetime: $99.99", callback_data="plan_lifetime")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your plan:", reply_markup=reply_markup)

# Handle subscription selection
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "plan_1month":
        await send_invoice(query, "1 Month Plan", 4.99, context)
    elif query.data == "plan_1year":
        await send_invoice(query, "1 Year Plan", 49.99, context)
    elif query.data == "plan_lifetime":
        await send_invoice(query, "Lifetime Plan", 99.99, context)

# Send invoice
async def send_invoice(query, title, price, context):
    prices = [LabeledPrice(label=title, amount=int(price * 100))]  # Amount in cents
    await context.bot.send_invoice(
        chat_id=query.message.chat_id,
        title=title,
        description=f"Subscription: {title}",
        payload=f"{title}_payload",
        provider_token="UQDHHuzmZSxLWHvAVLNHABWQ7cM611biQtuVnIJCZ4YqlWAo",  # Replace with your actual provider token
        currency="USD",
        prices=prices,
        start_parameter="subscription",
    )

