from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from IPython.display import Markdown, display
from llama_index.llms.openai import OpenAI
from chatbot_tavily import tavily_search
from llama_index.core import Document
from datetime import datetime
llm = OpenAI(model="gpt-4o-mini", api_key="api-key")  # Use environment variable for API key

mongo_uri = "mongodb+srv://andyblake:crs19981106@messagescluster.ci599.mongodb.net/?retryWrites=true&w=majority&appName=MessagesCluster"
db_name = "telegram_bot_db"
collection_name = "token_data"

host = mongo_uri
port = 27017

# Specify the required fields using dot notation
field_names = ["results"]



async def chat_bot(input_message):
   
    try:
         
        prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n
            You are a crypto advisor and expert researcher tasked with gathering information for a daily report.   Your current objective is to gather documents about : "https://dexscreener.com".\n
            you should tell very short and comprehensive answer to the following question: {input_message}
            write in markdown format within 500 words.
            """
        print("Generated prompt for TavilyClient:")
        print(prompt)
        text_list = await tavily_search(input_message)
        # if not documents:
        #     print("error______")
        #     return "No documents found for the given input."
       
        documents = [Document(text=t) for t in text_list]
        index = SummaryIndex.from_documents(documents)
        query_engine = index.as_query_engine(llm)  # Pass the LLM to the query engine

        query_text = prompt
        print(f"Querying for-----------------------: {query_text}")
        response =  query_engine.query(query_text)  # Use await here

        print("Query response received.----------------------")
        return response
       
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing your request."

# Usage example
# asyncio.run(chat_bot("What is the highest token price change in the last 24 hours?"))
