import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_age(token_created_at):
    # Convert token_created_at (milliseconds since epoch) to datetime
    token_creation_date = datetime.fromtimestamp(token_created_at / 1000.0)
    
    # Get current datepo
    current_date = datetime.now()
    
    # Calculate the difference using relativedelta
    delta = relativedelta(current_date, token_creation_date)
    
    # Format the age as needed
    age_parts = []
    if delta.years > 0:
        age_parts.append(f"{delta.years}y")
    if delta.months > 0:
        age_parts.append(f"{delta.months}m")
    if delta.days > 0:
        age_parts.append(f"{delta.days}d")
    
    # Join parts with a space
    token_age = " ".join(age_parts) if age_parts else "0d"  # Default to "0d" if no age is found
    
    return token_age

def format_number(value_string):
    """Format a number into a more readable string with K or M suffix."""
    try:
        # Attempt to convert the value_string to a float
        value = float(value_string)
    except (ValueError, TypeError):
        # Return 'N/A' or a default value if conversion fails
        return 'N/A'

    # Format the number based on its magnitude
    if value < 1_000:
        return f"{value:.0f}"  # Return as is if less than 1000
    elif value < 1_000_000:
        return f"{value / 1_000:.1f}K"  # Convert to thousands
    else:
        return f"{value / 1_000_000:.1f}M"  # Convert to millions

def get_token_prices():
    """Fetch current prices for ETH, SOL, and BNB (BSC) in USD."""
    tokens = {
        'ETH': 'ethereum',
        'BSC': 'binancecoin', 
        'SOL': 'solana'
    }
    
    prices = {}
    try:
        ids = ','.join(tokens.values())
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for symbol, coin_id in tokens.items():
                if coin_id in data:
                    prices[symbol] = data[coin_id]['usd']
                else:
                    prices[symbol] = None
        else:
            for symbol in tokens:
                prices[symbol] = None
    except Exception as e:
        print(f"Error fetching prices: {e}")
        for symbol in tokens:
            prices[symbol] = None
            
    print(prices)
    return prices

def convert_usd_to_crypto(usd_amount):
    """Convert USD amount to equivalent amounts in ETH, SOL, and BSC (BNB)."""
    prices = get_token_prices()
    conversions = {}
    
    for symbol, price in prices.items():
        if price:
            crypto_amount = usd_amount / price
            # Format with appropriate decimal places
            if symbol in ['ETH', 'BSC']:
                conversions[symbol] = round(crypto_amount, 4)
            else:  # SOL can use more decimal places
                conversions[symbol] = round(crypto_amount, 2)
        else:
            conversions[symbol] = None
            
    return conversions
