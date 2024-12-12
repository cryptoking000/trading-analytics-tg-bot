from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from subscribe import handle_wallet_input, handle_payment_verification
from apidata import fetch_trading_pair_data
from datetime import datetime
from database_function import db


def get_token_keyboard(chain_id, token_address):
    keyboard = [
        [
            InlineKeyboardButton("📈 View Chart", url=f"https://dexscreener.com/{chain_id}/{token_address}"),
            InlineKeyboardButton("💰 Buy Token", url=f"https://app.uniswap.org/#/swap?outputCurrency={token_address}")
        ]
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
        hex_data = update.message.text
        
        try:
            await update.message.chat.send_action(action="typing")
            
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