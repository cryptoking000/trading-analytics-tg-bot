from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from subscribe import handle_wallet_input, handle_payment_verification
from apidata import fetch_trading_pair_data
from datetime import datetime
from database_function import db
from chatbot import chat_bot
# from chatbot_tavily import tavily_search
from telegram.constants import ChatType, ParseMode
from messagecollection import message_collection
import asyncio

def get_token_keyboard(chain_id, token_address):
    keyboard = [
        [
            InlineKeyboardButton("📈 View Chart", url=f"https://dexscreener.com/{chain_id}/{token_address}"),
            InlineKeyboardButton("💰 Buy Token", url=f"https://app.uniswap.org/#/swap?outputCurrency={token_address}")
        ],
        # [
        #     InlineKeyboardButton("Subscribe", callback_data="subscribe")
        # ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def address_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    last_active = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.update_user_data(
        chat_id=update.message.chat_id,
        username=update.message.from_user.username, 
        last_active=last_active
    )
    
    current_state = context.user_data.get("current_state", "")
    
    if not context.user_data.get('subscribe_input_flag', False):
        input_message = update.message.text.strip()  # Get the token address from the message
        hex_data = ""
        print("🎄🎄input_message", input_message)
        
        for word in input_message.split():
            if len(word) >= 40 and word.isalnum(): 
                message_collection(update.message)
                hex_data = word
                # await update.message.reply_text(f'Token address received: {word}')  # Reply with the token address
              # await update.message.reply_text(f'this is normal word:{word}')
        if hex_data == "":  # this is a normal message
            if update.effective_chat.type == ChatType.PRIVATE:
                # output_message = await tavily_search(input_message)
                await update.message.chat.send_action(action="typing")
                await update.message.reply_text("🤔 Processing your request, please wait...")
                output_message = await chat_bot(input_message)           
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=output_message,
                    parse_mode=ParseMode.MARKDOWN
                )  
            else:
                pass
        else:#this is hex_data
            try:
                await update.message.chat.send_action(action="typing")
                print("🎄🎄hex_data", hex_data)
                trading_data, banner_url = await fetch_trading_pair_data(hex_data)
                chain_id = trading_data.split('\n')[1].split('@')[0].split()[-1]
                print("trading_data🎄🎄", trading_data)
                if banner_url:
                    await update.message.reply_photo(
                        photo=banner_url, 
                        caption=trading_data, 
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=get_token_keyboard(chain_id, hex_data)
                    )
                else:
                    await update.message.reply_text(
                        trading_data, 
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=get_token_keyboard(chain_id, hex_data)
                    )
            except Exception as e:
                await update.message.reply_text(
                        trading_data, 
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=get_token_keyboard(chain_id, hex_data)
                    )
    else:
        if current_state == "wallet_input":
            await handle_wallet_input(update, context, update.message.text.strip())
        elif current_state == "awaiting_payment":
            await handle_payment_verification(update, context, update.message.text.strip())