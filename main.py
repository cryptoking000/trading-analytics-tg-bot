from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from apidata import fetch_trading_pair_data

# This function handles received text messages and replies with trading data.
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Extract the hex data from the message text
    hex_data = update.message.text
    print(hex_data)
    # Fetch trading pair data for the given hex input
    trading_data = fetch_trading_pair_data(hex_data)
    # Reply back to the user with the fetched trading data
    await update.message.reply_text(f'Trading Data: {trading_data}')

# This function is triggered when the /hello command is used
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello, How are you?')
# Create the application with your bot's token
app = ApplicationBuilder().token("7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4").build()

# Adding handlers for specific commands and actions
app.add_handler(CommandHandler("hello", hello))  # Handles the /hello command
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))  # Processes any text that's not a command

# Start polling updates from Telegram
app.run_polling()
