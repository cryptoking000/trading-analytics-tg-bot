from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from llama_index.llms.openai import OpenAI
from datetime import datetime
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI LLM
llm = OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"), max_output_tokens=300)

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI")
db_name = "telegram_bot_db"
collection_name = "token_contracts"
host = mongo_uri
port = 27017

async def load_documents():
    field_names = ["all_data", "token_contracts"]
    reader = SimpleMongoReader(host, port)
    documents = await reader.load_data(db_name, collection_name, field_names)
    return documents

async def ai_insight(documents):
    try:
        prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n
            You are a crypto advisor tasked with gathering information for a daily report.  
            Identify unusual token patterns, price, and volume trends. Provide actionable insights in markdown format.
            Write differently every time within 500 characters.
            """
        index = SummaryIndex.from_documents(documents)
        query_engine = index.as_query_engine(llm=llm, streaming=True, similarity_top_k=5)
        
        print("Starting query...")
        start_time = datetime.now()
        response = await query_engine.query(prompt)  # Await the query execution
        end_time = datetime.now()
        
        print(f"Query response received in {end_time - start_time} seconds.")
        print(f"Query response: {response}")
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing your request."

async def main():
    start_time1 = datetime.now()
    documents = await load_documents()
    end_time1 = datetime.now()
    print("Loaded documents in:", end_time1 - start_time1)
    
    await ai_insight(documents)

# Run the main function
asyncio.run(main())
