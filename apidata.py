import requests
import json
from telegram import Bot, InputMediaPhoto
from math_function import calculate_age, format_number
async def fetch_trading_pair_data(pair_address):
    api_searchurl = f"https://api.dexscreener.com/latest/dex/search?q={pair_address}"
    response = requests.get(api_searchurl)
    if response.status_code == 200:
        data = response.json()
        pair_info = data.get('pairs')

        if pair_info and len(pair_info) > 0:
            data = pair_info[0]
            chain = data.get("chainId","N/A")
            name = data.get("baseToken", {}).get("name", "Unknown")
            symbol = data.get("baseToken", {}).get("symbol", "N/A")
            price = data.get("priceUsd", "N/A")
            dexid = data.get("dexId", "N/A")
            labels = data.get("labels", "N/A")
            fdv = data.get("fdv", "N/A")
            liquidity = data.get("liquidity", {}).get("usd", "N/A")
            base = data.get("liquidity", {}).get("base", "N/A")
            volume = data.get("volume", {}).get("usd24h", "N/A")
            ath = data.get("ath", "N/A")
            ath_time = data.get("athChange", {}).get("time", "N/A")
            one_hour_change = data.get("priceChange", {}).get("h1", "N/A")
            one_hour_volume = data.get("volume", {}).get("h1", "N/A")
            one_hour_buy_number = data.get("txns", {}).get("h1", {}).get("buys", "N/A")
            one_hour_sell_number = data.get("txns", {}).get("h1",{}).get("sells", "N/A")
            token_age = data.get("pairCreatedAt", "N/A")
            banner_url = data.get("info",{}).get("header", None)
            socials = data.get("info", {}).get("socials", [])
            websites = data.get("info", {}).get("websites", [])
            for website in websites:
                if website.get("label") == "Website":  # Check for the label "Website"
                    origin_url = website.get("url")  # Get the corresponding URL
                else:
                    origin_url == "https://"    
            # Loop through the socials to find the Telegram and Twitter URLs
            for social in socials:
                if social.get("type",None) == "telegram":
                    telegram_url = social.get("url")
                elif social.get("type") == "twitter":
                    twitter_url = social.get("url")
            result = (
                f"🟢 [{name}](https://t.me/CAMMT_bot?start={pair_address})[${format_number(fdv)}/4%] ${symbol}\n"
                f"🌍 {chain} @ {dexid} {labels}\n"
                f"💰 USD: `${price}`\n"
                f"💎 FDV: `${format_number(fdv)}`\n"
                f"💦 Liq: `${format_number(liquidity)}[x{base}]`\n"
                f"📊 Vol: `${format_number(volume)}`🕰️ Age:`{calculate_age(token_age)}`\n"
                f"⛰️ ATH: `${format_number(ath)} [{ath_time} ago]`\n"
                f"📈 1H: `{one_hour_change}%`⋅`${format_number(one_hour_volume)}`🅑`{one_hour_buy_number}`Ⓢ`{one_hour_sell_number}`\n"
                f"🧰 More:[🎨]({banner_url})[💬]({telegram_url})[🌍]({origin_url}) [🐦]({twitter_url})"
            )
            
            
            print(result)
            return result,banner_url
        else:
            print(f"No trading pair data found on {chain}.")
    else:
        print(f"Error: Failed to fetch data from {chain} (HTTP {response.status}).")
