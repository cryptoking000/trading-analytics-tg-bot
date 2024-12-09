from telegram import Update
from telegram.ext import ContextTypes, CallbackContext
from subscribe import handle_wallet_input, handle_payment_verification
from telegram.constants import ParseMode
from apidata import fetch_trading_pair_data
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
from database_function import db
# Define a custom filter for hexadecimal strings
def is_hexadecimal(text):
    try:
        int(text, 16)
        return True
    except ValueError:
        return False

def get_token_keyboard(chain_id, token_address):
    keyboard = [
        [
            InlineKeyboardButton("📈 View Chart", url=f"https://dexscreener.com/{chain_id}/{token_address}"),
            InlineKeyboardButton("💰 Buy Token", url=f"https://app.uniswap.org/#/swap?outputCurrency={token_address}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
# Bot command and message handlers
async def address_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    last_active = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.update_user_data(chat_id=update.message.chat_id,username=update.message.from_user.username, last_active=last_active)
    current_state = context.user_data.get("current_state", "")
    print("🎈🎈🎈c",context.user_data)
    if not context.user_data.get('subscribe_input_flag', False):
        hex_data = update.message.text
        print(f'hex_data: {hex_data}')
        
        try:
            # Send typing action while processing
            await update.message.chat.send_action(action="typing")
            
            # Fetch trading data
            trading_data, banner_url = await fetch_trading_pair_data(hex_data, update.message.chat_id)
            chain_id=trading_data.split('\n')[1].split('@')[0].split()[-1]
            if banner_url:
                # Send photo with caption
                await update.message.reply_photo(
                    photo=banner_url, 
                    caption=trading_data, 
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=get_token_keyboard(chain_id, hex_data)
                )
            else:
                # Send only text if no photo URL
                await update.message.reply_text(
                    trading_data, 
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=get_token_keyboard(chain_id, hex_data)
                )
        
        except Exception as e:
            await update.message.reply_text('Sorry, I was unable to fetch trading data. Please try again later.')
    else:
        if current_state == "wallet_input":
            await handle_wallet_input(update, context, update.message.text.strip())
        elif current_state == "awaiting_payment":
            await handle_payment_verification(update, context, update.message.text.strip())
async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("🎈🎈aaa🎈",context.user_data.get('subscribe_input_flag'))
    if not context.user_data.get('subscribe_input_flag'):
        await update.message.reply_text('Sorry, I don\'t understand that command. Please try again.')
    

    
# async def address_message_handler(update: Update, context: CallbackContext) -> None:
#     """Handle text replies from the user."""
    
#     #     chat_id = update.effective_chat.id
#     current_state = context.user_data.get("current_state", "")
    
#     print("🎈🎈🎈",context.user_data)
#     if context.user_data.get('subscribe_input_flag', True):
#         if current_state == "wallet_input":
#             await handle_wallet_input(update, context, update.message.text.strip())
#         elif current_state == "awaiting_payment":
#             await handle_payment_verification(update, context, update.message.text.strip())
