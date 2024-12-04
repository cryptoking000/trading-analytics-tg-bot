from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from apidata import fetch_trading_pair_data

from sendDM import send_dm
from payment import payment_start, button_handler


# Define a custom filter for hexadecimal strings
def is_hexadecimal(text):
    try:
        int(text, 16)
        return True
    except ValueError:
        return False


# Bot command and message handlers
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    hex_data = update.message.text
    print(hex_data)
    trading_data = fetch_trading_pair_data(hex_data)
    await update.message.reply_text(f'Trading Data: {trading_data}')


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello, How are you?')


async def start_sendDm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_dm()


async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await payment_start(update=update, context=context)


def main():
    application = ApplicationBuilder().token('7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4').build()

    # Add handlers
    application.add_handler(CommandHandler("hello", hello))
    application.add_handler(CommandHandler("start", start_payment))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'\A[0-9A-Fa-fx]+\Z'), reply))
    
    # Start the Bot
    application.run_polling()


if __name__ == '__main__':
    main()
