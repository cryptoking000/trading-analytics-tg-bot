import requests
import json

def load_chains(file_path):
    """Load blockchain data from a JSON file."""
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data.get('chains', [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading chains: {e}")
        return []

def fetch_trading_pair_data(pair_address):
    file_path = 'chains.json'
    chains = load_chains(file_path)
    """Fetch trading pair data for a given token address on specified blockchains."""
    for chain in chains:
        api_url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pair_address}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            # Debugging: Print out the whole response to understand its structure
            print(json.dumps(data, indent=4))

            # Check if 'pair' key exists and contains valid pair info
            pair_info = data.get('pair')
            
            if pair_info:
                price = pair_info.get('priceUsd', 'N/A')
                volume_24h = pair_info.get('volume', {}).get('h24', 'N/A')
                liquidity = pair_info.get('liquidity', {}).get('usd', 'N/A')
                fdv = pair_info.get('fdv', 'N/A')
                price_change_1h = pair_info.get('priceChange', {}).get('h1', 'N/A')
                ath = pair_info.get('allTimeHigh', {}).get('price', 'N/A')
                print(f"💰Price: ${price}\n"
                    f"💎FDV: ${fdv}\n"
                    f"💦Liquidity: ${liquidity}\n"
                    f"📊24h Volume: ${volume_24h}\n"
                    f"⛰️ATH: ${ath}\n"
                    f"📉1h Price Change: {price_change_1h}%")
                return (
                    f"💰Price: ${price}\n"
                    f"💎FDV: ${fdv}\n"
                    f"💦Liquidity: ${liquidity}\n"
                    f"📊24h Volume: ${volume_24h}\n"
                    f"⛰️ATH: ${ath}\n"
                    f"📉1h Price Change: {price_change_1h}%"
                )
            else:
                print(f"No trading pair data found on {chain}.")
        else:
            print(f"Error: Failed to fetch data from {chain} (HTTP {response.status_code}).")
    return "No data found for the specified trading pair."

# Specify the path to your JSON file containing blockchain information.

# pair_address = "0x8e2B762Bee3E2bf2C8fB0cdd04274042748D6C23"

# Fetch and print the trading pair data.
# result = fetch_trading_pair_data(pair_address)
# print(result)
