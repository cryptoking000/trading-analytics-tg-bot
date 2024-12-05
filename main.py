from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.constants import ParseMode

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
    print(f'hex_data: {hex_data}')
    
    try:
        # Fetch trading data
        trading_data = await fetch_trading_pair_data(hex_data)
        print(f'data--->{trading_data}')

        # Extract banner_url from the fetched data
        banner_url = trading_data[1]  # Replace with dynamic URL if available
       
        if banner_url:
            # Send photo with caption
            await update.message.reply_photo(photo=banner_url, caption=trading_data[0], parse_mode=ParseMode.MARKDOWN)
        else:
            # Send only text if no photo URL
            await update.message.reply_text(trading_data[0], parse_mode=ParseMode.MARKDOWN)
    
    except Exception as e:
        print(f'Error fetching trading data: {e}')
        await update.message.reply_text('Failed to fetch trading data.')


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello, How can I help with?')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hello, How `can` I help with? \n/start\n/hello')


async def start_sendDm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_dm()


async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await payment_start(update=update, context=context)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = (
       ' Run /help to see available commands.'

    )
    await update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN)

def main():
    application = ApplicationBuilder().token('7904308436:AAFDqx7xPPi59E7LI4Pe9GfniR1D9NGMTz4').build()

    # Add handlers
    application.add_handler(CommandHandler("hello", hello))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("subscribe", start_payment))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'\A[0-9A-Fa-fx]+\Z'), reply))
    
    # Start the Bot
    application.run_polling()


if __name__ == '__main__':
    main()
