from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from apidata import fetch_trading_pair_data


from sendDM import send_dm


app = ApplicationBuilder().token("7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4").build()

# Define a custom filter for hexadecimal strings
def is_hexadecimal(text):
    try:
        int(text, 16)
        return True
    except ValueError:
        return False


# Define the functions to be used by the bot commands and messages
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    hex_data = update.message.text
    print(hex_data)
    trading_data = fetch_trading_pair_data(hex_data)
    await update.message.reply_text(f'Trading Data: {trading_data}')

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello, How are you?')


# Handler to trigger the broadcast manually
async def start_sendDm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # if str(update.effective_user.id) == "6579613865":  # Optional: Restrict sendDming access
        await send_dm()

# Add handlers for commands and text messages
app.add_handler(CommandHandler("hello", hello))  # Handles the /hello command
app.add_handler(CommandHandler("start", start_sendDm))  # Handles the /hello command
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'\A[0-9A-Fa-f]+\Z') , reply))

# Start polling updates from Telegram
app.run_polling()
