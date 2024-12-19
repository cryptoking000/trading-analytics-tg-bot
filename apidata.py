import requests
import json
from telegram import Bot, InputMediaPhoto
from math_function import calculate_age, format_number
from datetime import datetime
from database_function import db
# def get_token_info(chain,token):  
#     url = f"https://api.coingecko.com/api/v3/coins/{chain}/contract/{token}"
#     response = requests.get(url)
#     data = response.json()
#     return data

# def get_ath(token):
#     BitQuery_url = "https://streaming.bitquery.io/eap"
#     headers = {
#         'Content-Type': 'application/json',
#         "X-API-KEY": ''
#         }  
    
#     payload = json.dumps({
#         "query": f"""
#             {{
#             Solana {{
#                 DEXTradeByTokens(
#                     where: {{Trade: {{Currency: {{MintAddress: {{is: "{token}"}}}}}}}}
#                     limit: {{count: 1}}
#                     orderBy: {{descending: Trade_PriceInUSD}}
#                     ) {{
#                     Trade {{
#                         price: PriceInUSD
#                         }}
#                     }}
#                 }}
#             }}
#         """,
#         "variables": "{}"
#         })

#     response = requests.request("POST", BitQuery_url, headers=headers, data = payload)
   
    
#     if response.status_code == 200:
#         data = response.json()
        
#         # Extract price if available
#         try:
#             price = data['data']['Solana']['DEXTradeByTokens'][0]['Trade']['price']
#             print(price)
#             return price
#         except (IndexError, KeyError):
#             print("No price data found.")
#             return 0
#     else:
#         print(f"Error fetching data: {response.status_code} - {response.text}")
#         return 0
    
async def fetch_trading_pair_data(pair_address):
    api_searchurl = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"
    try:
        # Add timeout and headers for more reliable requests
       
        print(f"Fetching data for pair address: {pair_address}")
        response = requests.get(api_searchurl, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        pair_info = data.get('pairs', [])
        
        if not pair_info:
            print("No pair info found, returning basic links")
            # Return just links if no pair data found
            links = (
                f"\n📌 *Analysis Tools*\n"
                f"[📊DexScreener](https://dexscreener.com/ethereum/{pair_address}) | "
                f"[🔍DexSpy](https://dexspy.io/ethereum/token/{pair_address}) | "
                f"[📈Defined](https://www.defined.fi/ethereum/{pair_address})\n"
                f"\n🔧 *Trading Tools*\n"
                f"[💱Simulator](https://t.me/TokenSimulatorBot?start={pair_address}) | "
                f"[📊Analytics](https://dexcheck.io/app/address-analyzer/{pair_address}?chain=ethereum) | "
                f"[📱DeBank](https://debank.com/profile/{pair_address})\n"
                f"\n🔍 *Security Tools*\n"
                f"[🛡️SusScan](https://t.me/SusScanbot?start={pair_address}) | "
                f"[🔐Arkham](https://platform.arkhamintelligence.com/explorer/address/{pair_address}) | "
                f"[⚠️DegenAlert](https://degenalert.xyz/degen-stats/wallet?a={pair_address})"
            )
            return links, None
            
        data = pair_info[0]
        print("Successfully retrieved pair data")
        
        # Extract data with improved error handling
        def safe_get(obj, *keys, default="N/A"):
            try:
                current = obj
                for key in keys:
                    current = current[key]
                return current if current is not None else default
            except (KeyError, TypeError):
                print(f"Failed to get value for keys {keys}")
                return default

        chain = safe_get(data, "chainId")
        name = safe_get(data, "baseToken", "name", default="Unknown")
        symbol = safe_get(data, "baseToken", "symbol")
        price = safe_get(data, "priceUsd")
        dexid = safe_get(data, "dexId")
        labels = safe_get(data, "labels", default="")
        fdv = safe_get(data, "fdv")
        liquidity = safe_get(data, "liquidity", "usd")
        base = safe_get(data, "liquidity", "base")
        quote = safe_get(data, "liquidity", "quote")
        volume = safe_get(data, "volume", "h24")
        # ath = get_ath(pair_address)
        ath_time = safe_get(data, "athChange", "time")
        one_hour_change = safe_get(data, "priceChange", "h1")
        one_hour_volume = safe_get(data, "volume", "h1")
        twentyfour_hour_change = safe_get(data, "priceChange", "h24")
        twentyfour_hour_volume = safe_get(data, "volume", "h24")
        one_hour_buy_number = safe_get(data, "txns", "h1", "buys")
        one_hour_sell_number = safe_get(data, "txns", "h1", "sells")
        twentyfour_hour_buy_number = safe_get(data, "txns", "h24", "buys")
        twentyfour_hour_sell_number = safe_get(data, "txns", "h24", "sells")
        token_age = safe_get(data, "pairCreatedAt")
        banner_url = safe_get(data, "info", "header")
        socials = safe_get(data, "info", "socials", default=[])
        websites = safe_get(data, "info", "websites", default=[])

        print(f"Processing token: {name} ({symbol})")

        # Initialize with better default values
        origin_url = next((website.get("url") for website in websites if website.get("label") == "Website"), "#")
        telegram_url = next((social.get("url") for social in socials if social.get("type") == "telegram"), "#")
        twitter_url = next((social.get("url") for social in socials if social.get("type") == "twitter"), "#")

        print("Formatting token information")
        # Enhanced token info formatting
        token_info = (
            f"🟢 [{name}](https://t.me/CAMMT_bot?start={pair_address})[${format_number(fdv)}/4%] ${symbol}\n"
            f"🌍 {chain} @ {dexid} {labels}\n"
            f"💰 Price: `${price}`\n"
            f"💎 FDV: `${format_number(fdv)}`\n"
            f"💦 Liquidity: `${format_number(liquidity)}[x{base}x{quote}]`\n"
            f"📊 Volume 24h: `${format_number(volume)}` | Age: `{calculate_age(token_age)}`\n"
            # f"⛰️ ATH: `${ath} [{ath_time} ago]`\n"
            f"📈 1H Change: `{format_number(one_hour_change)}%` | Vol: `${format_number(one_hour_volume)}`\n"
            f"📈 24H Change: `{format_number(twentyfour_hour_change)}%` | Vol: `${format_number(twentyfour_hour_volume)}`\n"
            f"📊 1H Trades: 🟢`{format_number(one_hour_buy_number)}` | 🔴`{format_number(one_hour_sell_number)}`\n"
            f"📊 24H Trades: 🟢`{format_number(twentyfour_hour_buy_number)}` | 🔴`{format_number(twentyfour_hour_sell_number)}`\n\n"
            # f"🖨️Mint:{'✅' if minted else '❌'} | LP 🔥({format_number(lp_burn_amount)}%)"
            f"🔗 Links: [📊Chart]({banner_url}) [💬TG]({telegram_url}) [🌐Web]({origin_url}) [🐦Twitter]({twitter_url})\n"
            f"\n`{pair_address}`\n"
            f"\n📌 *Analysis Tools*\n"
            f"[📊DexScreener](https://dexscreener.com/{chain}/{pair_address}) | "
            f"[🔍DexSpy](https://dexspy.io/{chain}/token/{pair_address}) | "
            f"[📈Defined](https://www.defined.fi/{chain}/{pair_address})\n"
            f"\n🔧 *Trading Tools*\n"
            f"[💱Simulator](https://t.me/TokenSimulatorBot?start={pair_address}) | "
            f"[📊Analytics](https://dexcheck.io/app/address-analyzer/{pair_address}?chain={chain}) | "
            f"[📱DeBank](https://debank.com/profile/{pair_address})\n"
            f"\n🔍 *Security Tools*\n"
            f"[🛡️SusScan](https://t.me/SusScanbot?start={pair_address}) | "
            f"[🔐Arkham](https://platform.arkhamintelligence.com/explorer/address/{pair_address}) | "
            f"[⚠️DegenAlert](https://degenalert.xyz/degen-stats/wallet?a={pair_address})"
        
        
        )

       
       

        print("Successfully prepared response")
        return token_info , banner_url

    except requests.RequestException as e:
        print(f"Network error occurred: {str(e)}")
        # Return just links on network error
        links = (
            f"\n📌 *Analysis Tools*\n"
            f"[📊DexScreener](https://dexscreener.com/ethereum/{pair_address}) | "
            f"[🔍DexSpy](https://dexspy.io/ethereum/token/{pair_address}) | "
            f"[📈Defined](https://www.defined.fi/ethereum/{pair_address})\n"
            f"\n🔧 *Trading Tools*\n"
            f"[💱Simulator](https://t.me/TokenSimulatorBot?start={pair_address}) | "
            f"[📊Analytics](https://dexcheck.io/app/address-analyzer/{pair_address}?chain=ethereum) | "
            f"[📱DeBank](https://debank.com/profile/{pair_address})\n"
            f"\n🔍 *Security Tools*\n"
            f"[🛡️SusScan](https://t.me/SusScanbot?start={pair_address}) | "
            f"[🔐Arkham](https://platform.arkhamintelligence.com/explorer/address/{pair_address}) | "
            f"[⚠️DegenAlert](https://degenalert.xyz/degen-stats/wallet?a={pair_address})"
        )
        return links, None
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        # Return just links on any other error
        links = (
            f"\n📌 *Analysis Tools*\n"
            f"[📊DexScreener](https://dexscreener.com/ethereum/{pair_address}) | "
            f"[🔍DexSpy](https://dexspy.io/ethereum/token/{pair_address}) | "
            f"[📈Defined](https://www.defined.fi/ethereum/{pair_address})\n"
            f"\n🔧 *Trading Tools*\n"
            f"[💱Simulator](https://t.me/TokenSimulatorBot?start={pair_address}) | "
            f"[📊Analytics](https://dexcheck.io/app/address-analyzer/{pair_address}?chain=ethereum) | "
            f"[📱DeBank](https://debank.com/profile/{pair_address})\n"
            f"\n🔍 *Security Tools*\n"
            f"[🛡️SusScan](https://t.me/SusScanbot?start={pair_address}) | "
            f"[🔐Arkham](https://platform.arkhamintelligence.com/explorer/address/{pair_address}) | "
            f"[⚠️DegenAlert](https://degenalert.xyz/degen-stats/wallet?a={pair_address})"
        )
        return links, None
