from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from math_function import convert_usd_to_crypto
import aiohttp
import logging
from database_function import UserDatabaseManager
from datetime import datetime, timedelta
from database_function import db
# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize database manager
db_manager = UserDatabaseManager()

# Constants
WALLET_ADDRESSES = {
    "BSC": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
    "ETH": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", 
    "SOL": "8njqnN9ZRQkvUFPNzjEU1mXMfPrC54zugmUeZoAYR659"
}

# Define keyboards
def get_duration_keyboard():
    print("Getting duration keyboard")
    return [
        [
            InlineKeyboardButton("1 Month ($50)", callback_data="duration:1:50"),
            InlineKeyboardButton("3 Months ($120)", callback_data="duration:3:120")
        ],
        [InlineKeyboardButton("1 Year ($500)", callback_data="duration:12:500")]
    ]

def get_payment_keyboard():
    print("Getting payment keyboard")
    return [
        [
            InlineKeyboardButton("BSC", callback_data="pay:BSC"),
            InlineKeyboardButton("ETH", callback_data="pay:ETH"),
            InlineKeyboardButton("SOL", callback_data="pay:SOL")
        ],
        [InlineKeyboardButton("Back", callback_data="back")]
    ]

async def payment_start(update: Update, context: CallbackContext):
    """Initialize the subscription process."""
    print(f"Starting payment process for chat_id: {update.effective_chat.id}")
    keyboard = get_duration_keyboard()
    message = (
        "🔥 *Premium Subscription Plans*\n\n"
        "Choose your subscription duration:\n"
        "• Access to real-time market analysis\n"
        "• AI-powered price predictions\n" 
        "• Priority support\n"
        "• Exclusive trading signals"
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

    context.user_data["current_state"] = "duration_selection"
    print(f"Set state to duration_selection for chat_id: {update.effective_chat.id}")

async def button_handler(update: Update, context: CallbackContext):
    """Handle button clicks."""
    query = update.callback_query
    await query.answer()

    current_state = context.user_data.get("current_state", "")
    chat_id = update.effective_chat.id
    print(f"Button handler called - State: {current_state}, Chat ID: {chat_id}")

    if current_state == "duration_selection" and query.data.startswith("duration:"):
        _, duration, price = query.data.split(":")
        print(f"Duration selected: {duration} months, Price: ${price}")
        context.user_data.update({
            "duration": int(duration),
            "price": float(price),
            "current_state": "wallet_input"
        })

        message = (
            "Please enter your wallet address for receiving rewards.\n\n"
            "This wallet will be used for future reward distributions and premium features."
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=message
        )
    elif current_state == "payment_selection" and query.data.startswith("pay:"):
        chain = query.data.split(":")[1]
        price_usd = context.user_data.get("price", 0)
        duration = context.user_data.get("duration", 1)
        wallet_address = context.user_data.get("wallet_address")
        print(f"Payment chain selected: {chain}, Amount: ${price_usd}")
        
        try:
            crypto_amounts = convert_usd_to_crypto(price_usd)
            expected_amount = crypto_amounts.get(chain)
            expiry_date = datetime.now() + timedelta(days=duration * 30)
            print(f"Crypto amount: {expected_amount} {chain}, Expiry: {expiry_date}")

            keyboard = [
                [InlineKeyboardButton("I've Sent Payment", callback_data="payment_sent")],
                [InlineKeyboardButton("Cancel", callback_data="back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = (
                f"💳 *Payment Details*\n\n"
                f"Amount: {expected_amount} {chain} (${price_usd})\n"
                f"Send to address:\n`{WALLET_ADDRESSES[chain]}`\n\n"
                f"Your reward wallet:\n`{wallet_address}`\n\n"
                f"Duration: {duration} {'month' if duration == 1 else 'months'}\n"
                f"Expires: {expiry_date.strftime('%Y-%m-%d')}\n\n"
                "After sending payment, click 'I've Sent Payment' and provide the transaction hash."
            )
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
            context.user_data.update({
                "expected_amount": expected_amount,
                "payment_chain": chain,
                "current_state": "awaiting_payment",
                "expiry_date": expiry_date
            })
            print("Payment details sent and state updated to awaiting_payment")
            
        except Exception as e:
            logging.error(f"Payment setup error: {e}")
            print(f"Error in payment setup: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Error setting up payment. Please try again or contact support."
            )

    elif current_state == "wallet_input":
        wallet_address = update.message.text.strip()
        print(f"Processing wallet address: {wallet_address}")
        if len(wallet_address) < 10:  # Basic validation for wallet address length
            await update.message.reply_text("❌ Invalid wallet address. Please try again.")
            print("Invalid wallet address detected")
            return

        context.user_data["wallet_address"] = wallet_address
        print(f"Wallet address saved: {wallet_address}")
        # Save wallet address to the database
        db.add_user(chat_id=chat_id, wallet_address=wallet_address)
        print("Wallet address saved to database")
        
        context.user_data["current_state"] = "payment_selection"

        # Provide the next step (payment chain selection)
        keyboard = get_payment_keyboard()
        await update.message.reply_text(
            "✅ Wallet address saved! Now select your preferred payment chain:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "back":
        print("User clicked back button")
        keyboard = get_duration_keyboard()
        message = "Select your subscription duration:"
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=reply_markup
        )
        context.user_data["current_state"] = "duration_selection"
        print("State reset to duration_selection")

    else:
        print(f"Invalid action detected: {query.data}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Invalid action. Please try again."
        )

async def message_handler(update: Update, context: CallbackContext):
    """Handle text replies from the user."""
    current_state = context.user_data.get("current_state", "")
    chat_id = update.effective_chat.id
    print(f"Message handler called - State: {current_state}, Chat ID: {chat_id}")

    if current_state == "wallet_input":
        wallet_address = update.message.text
        print(f"Processing wallet address input: {wallet_address}")
        context.user_data["wallet_address"] = wallet_address
        
        # Save wallet address to database
        db.add_user(chat_id=chat_id, wallet_address=wallet_address)
        print("Wallet address saved to database")
        
        price_usd = context.user_data.get("price", 0)
        duration = context.user_data.get("duration", 1)
        chain = "BSC"  # Default chain
        print(f"Setting up payment details - Price: ${price_usd}, Duration: {duration} months")
        
        try:
            crypto_amounts = convert_usd_to_crypto(price_usd)
            expected_amount = crypto_amounts.get(chain)
            expiry_date = datetime.now() + timedelta(days=duration * 30)
            print(f"Calculated amount: {expected_amount} {chain}, Expiry: {expiry_date}")

            keyboard = [
                [InlineKeyboardButton("I've Sent Payment", callback_data="payment_sent")],
                [InlineKeyboardButton("Cancel", callback_data="back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            message = (
                f"💳 *Payment Details*\n\n"
                f"Amount: {expected_amount} {chain} (${price_usd})\n"
                f"Send to address:\n`{WALLET_ADDRESSES[chain]}`\n\n"
                f"Your reward wallet:\n`{wallet_address}`\n\n"
                f"Duration: {duration} {'month' if duration == 1 else 'months'}\n"
                f"Expires: {expiry_date.strftime('%Y-%m-%d')}\n\n"
                "After sending payment, click 'I've Sent Payment' and provide the transaction hash."
            )
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            
            context.user_data.update({
                "expected_amount": expected_amount,
                "payment_chain": chain,
                "current_state": "awaiting_payment",
                "expiry_date": expiry_date
            })
            print("Payment details sent and state updated to awaiting_payment")
            
        except Exception as e:
            logging.error(f"Payment setup error: {e}")
            print(f"Error in payment setup: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="Error setting up payment. Please try again or contact support."
            )

    elif current_state == "awaiting_payment":
        tx_hash = update.message.text.strip()
        print(f"Processing transaction hash: {tx_hash}")
        if len(tx_hash) < 10:  # Basic validation for hash length
            print("Invalid transaction hash detected")
            await update.message.reply_text("❌ Invalid transaction hash. Please try again.")
            return

        chain = context.user_data.get("payment_chain", "")
        expected_amount = context.user_data.get("expected_amount", 0)
        payment_address = WALLET_ADDRESSES.get(chain)
        print(f"Verifying transaction - Chain: {chain}, Expected amount: {expected_amount}")

        await update.message.reply_text("🔍 Verifying your transaction, please wait...")

        is_valid = await verify_transaction(chain, tx_hash, expected_amount, payment_address)
        print(f"Transaction verification result: {is_valid}")

        if is_valid:
            try:
                expiry_date = context.user_data.get("expiry_date")
                db_manager.update_user_payment(
                    chat_id=chat_id,
                    paid=True,
                    transaction_hash=tx_hash,
                    expired_time=expiry_date.strftime('%Y-%m-%d %H:%M:%S')
                )
                print(f"Payment verified and database updated for chat_id: {chat_id}")
                await update.message.reply_text(
                    "✅ Payment verified successfully!\n\n"
                    "Your premium subscription is now active. Enjoy your enhanced features!\n"
                    f"Subscription expires: {expiry_date.strftime('%Y-%m-%d')}"
                )
                context.user_data.clear()  # Clear user data
                print("User data cleared")
            except Exception as e:
                logging.error(f"Database error: {e}")
                print(f"Database error: {e}")
                await update.message.reply_text("❌ Error updating subscription. Please contact support.")
        else:
            print("Transaction verification failed")
            await update.message.reply_text(
                "❌ Transaction verification failed.\n"
                "Please ensure you've sent the correct amount and provided the correct transaction hash."
            )

async def verify_transaction(chain: str, tx_hash: str, expected_amount: float, expected_address: str) -> bool:
    """Verify the transaction based on the chain."""
    print(f"Starting transaction verification - Chain: {chain}, Hash: {tx_hash}")
    try:
        async with aiohttp.ClientSession() as session:
            if chain == "SOL":
                print("Verifying Solana transaction")
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
                        print(f"SOL transaction details - Amount: {tx_amount}, To: {tx_to}")
                        return abs(tx_amount - expected_amount) < 0.01 and tx_to == expected_address

            elif chain in ("BSC", "ETH"):
                print(f"Verifying {chain} transaction")
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
                        print(f"{chain} transaction details - Amount: {tx_amount}, To: {tx_to}")
                        return abs(tx_amount - expected_amount) < 0.0001 and tx_to.lower() == expected_address.lower()
    except Exception as e:
        logging.error(f"Error verifying transaction: {e}")
        print(f"Transaction verification error: {e}")
        return False
    print("Transaction verification failed or unsupported chain")
    return False
