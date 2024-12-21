from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from IPython.display import Markdown, display
from llama_index.llms.openai import OpenAI
# from chatbot_tavily import tavily_search
from llama_index.core import Document
import asyncio
from datetime import datetime
import os
import json
from dotenv import load_dotenv
load_dotenv()

llm = OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))  # Use environment variable for API key

mongo_uri = os.getenv("MONGO_URI")
db_name = "telegram_bot_db"
collection_name = "token_contracts"

host = mongo_uri
port = 27017

# Specify the required fields using dot notation
field_names = ["all_data","token_contracts"]

# Local file path to store MongoDB data
LOCAL_DATA_FILE = "mongo_data.json"

async def chat_bot(input_message):
   
    try:
        # Check if local file exists and is not older than 24 hours
        should_fetch_from_mongo = True
        if os.path.exists(LOCAL_DATA_FILE):
            file_time = datetime.fromtimestamp(os.path.getmtime(LOCAL_DATA_FILE))
            if (datetime.now() - file_time).days < 1:
                should_fetch_from_mongo = False

        if should_fetch_from_mongo:
            # Fetch from MongoDB and save locally
            reader = SimpleMongoReader(host, port)
            print("loading data from mongodb...")
            documents = reader.load_data(
                db_name, collection_name, field_names
            )
            
            # Save to local file
            with open(LOCAL_DATA_FILE, 'w') as f:
                json.dump([doc.to_dict() for doc in documents], f)
        else:
            # Load from local file
            print("loading data from local file...")
            with open(LOCAL_DATA_FILE, 'r') as f:
                data = json.load(f)
                documents = [Document.from_dict(doc) for doc in data]
         
        prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n
            You are a crypto advisor and expert researcher tasked with gathering information for a daily report.   Your current objective is to gather documents about : "https://dexscreener.com".\n
            you should tell very short and comprehensive answer to the following question: {input_message}
            write in markdown format within 500 words.
            """
        
        print("Documents loaded successfully.")
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
if __name__ == "__main__":
    # Example usage
    input_message = "What are the top 5 tokens with the highest market cap?"
    response = asyncio.run(chat_bot(input_message))
    print(response)