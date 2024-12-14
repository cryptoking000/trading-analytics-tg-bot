from tavily import TavilyClient
from datetime import datetime

# Step 1. Instantiating your TavilyClient
tavily_client = TavilyClient(api_key="tvly-api")

# Step 2. Executing a simple search query
async def tavily_search(query):
    print(query)
    prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n
        You are a crypto advisor and expert researcher tasked with gathering information for a daily report.   Your current objective is to gather documents about : "https://dexscreener.com".\n
        you should tell very short and comprehensive answer to the following question: {query}
        write in markdown format within 500 words.
        """
    print(prompt)
    # response = tavily_client.search(query)
    # response = tavily_client.get_search_context(query)
    # answer = tavily_client.qna_search(query)
    answer = tavily_client.search("who is the best crypto investor in the world")
    print(answer)
    return answer
# Step 3. That's it! You've done a Tavily Search!
# answer = tavily_client.search("who is the best crypto investor in the world")
# print(answer)