import requests
import json
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
mongo_client = MongoClient(mongo_uri)
db = mongo_client["telegram_bot_db"]
token_list_collection = db["token_list_collection"]
token_data_collection = db["token_data_collection"]
eth_json_file = "https://raw.githubusercontent.com/jab416171/uniswap-pairtokens/master/uniswap_pair_tokens.json"



def fetch_eth_json_file():
    """Fetch token data from GitHub repository"""
    try:
        response = requests.get(eth_json_file)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return {}

def get_token_addresses():
    """Fetch token addresses and store them in MongoDB"""
    eth_json_data = fetch_eth_json_file()
    addresses = [token['address'] for token in eth_json_data.get('tokens', []) if 'address' in token]
    
    # Save addresses as a single JSON object
    if addresses:
        # Remove existing entries before inserting new ones
        token_list_collection.delete_many({})
        token_list_collection.insert_one({"addresses": addresses})
        print(f"Successfully saved {len(addresses)} token addresses to database")
    else:
        print("Warning: No addresses found to save")
    
    return addresses
def get_token_data():
    token_list_collection = db["token_list_collection"]
    addresses = token_list_collection.find_one({})["addresses"]
    token_data_collection.delete_many({})
    for address in addresses:
        api_searchurl = f"https://api.dexscreener.com/latest/dex/search?q={address}"
        try:
            print(f"Fetching data for pair address: {address}")
            response = requests.get(api_searchurl, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            token_data_collection.insert_one({"data": data})
            print(f"Successfully saved {len(data)} token data to database")
        except Exception as e:
            print(f"Error occurred: {e}")

if __name__ == "__main__":
    try:
        print("Fetching token data...")
        get_token_data()
        print("success")
        # print("Fetching token addresses...")
        # addresses = get_token_addresses()
        # print(f"Successfully retrieved {len(addresses)} token addresses")
    except Exception as e:
        print(f"Error occurred: {e}")
        mongo_client.close()
