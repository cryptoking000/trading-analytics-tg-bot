from tavily import TavilyClient
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()
tavily_api_key = os.getenv("TAVILY_API_KEY")
# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key=tavily_api_key)

# Step 2. Executing a simple search query
async def tavily_search(query):
    print("Starting search for query:", query)
   
    
   
    print("Sending prompt to TavilyClient...")
    answer = tavily_client.qna_search(query)
    print("✨🎉✨", answer)
    
    text_list = []
    for document in answer['results']:
        print("document---------",document['content'])
        # if isinstance(document, dict) and 'result' in document:
        text_list.append(document['content'])
    print("✨🎉✨", text_list)
    return text_list
    # text_list = []
    # url = "https://dexscreener.com/solana/"
    # document = tavily_client.extract(url)
    # print(document)
    # text_list.append(document['results']['content'])
    # print(text_list)
    # return text_list

# if __name__ == "__main__":
#     print("Starting the asyncio event loop...")
#     asyncio.run(tavily_search("who is the best crypto investor in the world"))
#     print("Search completed.")
