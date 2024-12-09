from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes

from math_function import convert_usd_to_crypto
import aiohttp
import logging
from database_function import UserDatabaseManager, db
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
from decimal import Decimal
import asyncio
from functools import wraps

# Setup logging with file only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('subscription.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize database manager
db_manager = UserDatabaseManager()

# Enhanced Constants with more options
WALLET_ADDRESSES: Dict[str, str] = {
    "BSC": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    "ETH": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 
    "SOL": "8njqnN9ZRQkvUFPNzjEU1mXMfPrC54zugmUeZoAYR659",
    "TON": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
}

SUBSCRIPTION_PLANS = [
    {"duration": 1, "price": 50, "label": "1 Month", "discount": 0},
    {"duration": 3, "price": 120, "label": "3 Months", "discount": 20},
    {"duration": 12, "price": 500, "label": "1 Year", "discount": 30}
]

SUPPORTED_CHAINS = list(WALLET_ADDRESSES.keys())
MIN_WALLET_LENGTH = 10
MIN_TX_HASH_LENGTH = 10
MAX_RETRIES = 3
RETRY_DELAY = 2

def retry_on_failure(max_retries: int = MAX_RETRIES, delay: int = RETRY_DELAY):
    """Decorator to retry functions on failure"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Attempt {i+1} failed: {str(e)}")
                    if i < max_retries - 1:
                        await asyncio.sleep(delay)
            return False
        return wrapper
    return decorator

def get_duration_keyboard() -> List[List[InlineKeyboardButton]]:
    """Generate enhanced keyboard for subscription duration selection with discounts."""
    keyboard = []
    row = []
    for i, plan in enumerate(SUBSCRIPTION_PLANS):
        display_text = f"{plan['label']} (${plan['price']}"
        if plan['discount'] > 0:
            display_text += f" - {plan['discount']}% OFF)"
        else:
            display_text += ")"
            
        button = InlineKeyboardButton(
            display_text,
            callback_data=f"duration:{plan['duration']}:{plan['price']}"
        )
        row.append(button)
        if len(row) == 2 or i == len(SUBSCRIPTION_PLANS) - 1:
            keyboard.append(row)
            row = []
    return keyboard

def get_payment_keyboard() -> List[List[InlineKeyboardButton]]:
    """Generate enhanced keyboard for payment chain selection."""
    keyboard = []
    row = []
    for i, chain in enumerate(SUPPORTED_CHAINS):
        row.append(InlineKeyboardButton(chain, callback_data=f"pay:{chain}"))
        if len(row) == 3 or i == len(SUPPORTED_CHAINS) - 1:
            keyboard.append(row)
            row = []
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    return keyboard

async def payment_start(update: Update, context: CallbackContext) -> None:
    """Initialize the enhanced subscription process."""
    chat_id = update.effective_chat.id
    logger.info(f"Starting payment process for chat_id: {chat_id}")
    print("🎈",context.user_data)
    keyboard = get_duration_keyboard()
    message = (
        "🔥 *Premium Subscription Plans*\n\n"
        "Choose your subscription duration:\n\n"
        "✨ *Benefits Include:*\n"
        "• Real-time market analysis and alerts\n"
        "• Advanced AI-powered price predictions\n"
        "• Priority 24/7 support\n"
        "• Exclusive trading signals\n"
        "• Custom portfolio tracking\n"
        "• Risk management tools\n\n"
        "🎉 *Special Offer:*\n"
        "• Save up to 30% on longer subscriptions!"
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=message,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data["current_state"] = "duration_selection"

async def handle_duration_selection(update: Update, context: CallbackContext, duration: int, price: float) -> None:
    """Handle enhanced duration selection callback."""
    chat_id = update.effective_chat.id
    
    selected_plan = next((plan for plan in SUBSCRIPTION_PLANS if plan['duration'] == duration), None)
    if selected_plan and selected_plan['discount'] > 0:
        original_price = price
        price = price * (100 - selected_plan['discount']) / 100
        context.user_data['discount_applied'] = selected_plan['discount']
        context.user_data['original_price'] = original_price

    context.user_data.update({
        "duration": duration,
        "price": Decimal(str(price)),
        "current_state": "payment_selection",
        "selection_timestamp": datetime.now().isoformat()
    })

    keyboard = get_payment_keyboard()
    message = "Select your preferred payment chain:"
    await context.bot.send_message(
        chat_id=chat_id, 
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_payment_chain_selection(update: Update, context: CallbackContext, chain: str) -> None:
    """Handle payment chain selection callback."""
    chat_id = update.effective_chat.id
    
    context.user_data.update({
        "payment_chain": chain,
        "current_state": "wallet_input"
    })
    
    message = (
        "Please enter your wallet address for receiving rewards.\n\n"
        "This wallet will be used for future reward distributions and premium features."
    )
    await context.bot.send_message(chat_id=chat_id, text=message)

async def handle_wallet_input(update: Update, context: CallbackContext, wallet_address: str) -> None:
    """Handle wallet address input."""
    chat_id = update.effective_chat.id
    
    if len(wallet_address) < MIN_WALLET_LENGTH:
        await update.message.reply_text("❌ Invalid wallet address. Please try again.")
        return
    
    try:
        price_usd = context.user_data.get("price", 0)
        duration = context.user_data.get("duration", 1)
        chain = context.user_data.get("payment_chain")
        
        crypto_amounts = convert_usd_to_crypto(float(price_usd))
        expected_amount = crypto_amounts.get(chain)
        expiry_date = datetime.now() + timedelta(days=duration * 30)

        context.user_data.update({
            "wallet_address": wallet_address,
            "expected_amount": expected_amount,
            "current_state": "awaiting_payment",
            "expiry_date": expiry_date
        })

        db.update_user_payment(chat_id=chat_id, wallet_address=wallet_address, payment_method=chain)

        keyboard = [
            [InlineKeyboardButton("I've Sent Payment", callback_data="payment_sent")],
            [InlineKeyboardButton("Cancel", callback_data="back")]
        ]

        message = (
            f"💳 *Payment Details*\n\n"
            f"Amount: {expected_amount} {chain} (${price_usd})\n"
            f"Send to address:\n`{WALLET_ADDRESSES[chain]}`\n\n"
            f"Your reward wallet:\n`{wallet_address}`\n\n"
            f"Duration: {duration} {'month' if duration == 1 else 'months'}\n"
            f"Expires: {expiry_date.strftime('%Y-%m-%d')}\n\n"
            "After sending payment, click 'I've Sent Payment' and provide the transaction hash."
        )

        await update.message.reply_text(
            text=message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        logger.error(f"Error processing wallet for chat_id {chat_id}: {str(e)}")
        await update.message.reply_text("❌ Error processing wallet. Please try again.")

async def button_handler(update: Update, context: CallbackContext) -> None:
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    current_state = context.user_data.get("current_state", "")

    if current_state == "duration_selection" and query.data.startswith("duration:"):
        _, duration, price = query.data.split(":")
        await handle_duration_selection(update, context, int(duration), float(price))
    
    elif current_state == "payment_selection" and query.data.startswith("pay:"):
        chain = query.data.split(":")[1]
        await handle_payment_chain_selection(update, context, chain)
    
    elif query.data == "back":
        keyboard = get_duration_keyboard()
        await context.bot.send_message(
            chat_id=chat_id,
            text="Select your subscription duration:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        context.user_data["current_state"] = "duration_selection"
    
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Invalid action. Please try again."
        )

async def handle_payment_verification(update: Update, context: CallbackContext, tx_hash: str) -> None:
    """Handle payment verification."""
    chat_id = update.effective_chat.id
    
    if len(tx_hash) < MIN_TX_HASH_LENGTH:
        await update.message.reply_text("❌ Invalid transaction hash. Please try again.")
        return

    chain = context.user_data.get("payment_chain", "")
    expected_amount = context.user_data.get("expected_amount", 0)
    payment_address = WALLET_ADDRESSES.get(chain)

    await update.message.reply_text("🔍 Verifying your transaction, please wait...")

    is_valid = await verify_transaction(chain, tx_hash, expected_amount, payment_address)
    
    if is_valid:
        try:
            expiry_date = context.user_data.get("expiry_date")
            db_manager.update_user_payment(
                chat_id=chat_id,
                paid=True,
                transaction_hash=tx_hash,
                expired_time=expiry_date.strftime('%Y-%m-%d %H:%M:%S')
            )
            
            await update.message.reply_text(
                "✅ Payment verified successfully!\n\n"
                "Your premium subscription is now active. Enjoy your enhanced features!\n"
                f"Subscription expires: {expiry_date.strftime('%Y-%m-%d')}"
            )
            context.user_data.clear()
            
        except Exception as e:
            logger.error(f"Database error for chat_id {chat_id}: {str(e)}")
            await update.message.reply_text("❌ Error updating subscription. Please contact support.")
    else:
        await update.message.reply_text(
            "❌ Transaction verification failed.\n"
            "Please ensure you've sent the correct amount and provided the correct transaction hash."
        )

@retry_on_failure()
async def verify_transaction(chain: str, tx_hash: str, expected_amount: float, expected_address: str) -> bool:
    """Verify the transaction based on the chain."""
    try:
        async with aiohttp.ClientSession() as session:
            if chain == "SOL":
                return await verify_solana_transaction(session, tx_hash, expected_amount, expected_address)
            elif chain in ("BSC", "ETH", "TON"):
                return await verify_evm_transaction(session, chain, tx_hash, expected_amount, expected_address)
    except Exception as e:
        logger.error(f"Error verifying {chain} transaction: {str(e)}")
        return False
    return False

@retry_on_failure()
async def verify_solana_transaction(session: aiohttp.ClientSession, tx_hash: str, 
                                  expected_amount: float, expected_address: str) -> bool:
    """Verify Solana transaction."""
    url = "https://api.mainnet-beta.solana.com"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params": [tx_hash, {"encoding": "json", "commitment": "confirmed"}]
    }
    
    async with session.post(url, json=payload) as response:
        data = await response.json()
        if data.get("result"):
            tx_details = data["result"]
            tx_amount = (tx_details["meta"]["postBalances"][1] - tx_details["meta"]["preBalances"][1]) / 1e9
            tx_to = tx_details["transaction"]["message"]["accountKeys"][1]
            return abs(tx_amount - expected_amount) < 0.01 and tx_to == expected_address
    return False

@retry_on_failure()
async def verify_evm_transaction(session: aiohttp.ClientSession, chain: str, tx_hash: str,
                               expected_amount: float, expected_address: str) -> bool:
    """Verify EVM-based transaction (ETH/BSC/TON)."""
    api_key = "YOUR_API_KEY"  # Replace with actual API key
    api_url = f"https://api.{chain.lower()}scan.com/api"
    params = {
        "module": "proxy",
        "action": "eth_getTransactionByHash",
        "txhash": tx_hash,
        "apikey": api_key
    }
    
    async with session.get(api_url, params=params) as response:
        data = await response.json()
        if data.get("result"):
            tx_details = data["result"]
            tx_amount = int(tx_details["value"], 16) / 1e18
            tx_to = tx_details["to"]
            return abs(tx_amount - expected_amount) < 0.0001 and tx_to.lower() == expected_address.lower()
    return False
