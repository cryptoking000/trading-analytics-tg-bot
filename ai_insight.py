from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from llama_index.llms.openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio
# from llama_index.vector_stores import FaissVectorStore
load_dotenv()

llm = OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"), max_output_tokens=300)  # Use environment variable for API key
mongo_uri = os.getenv("MONGO_URI")
db_name = "telegram_bot_db"
collection_name = "token_contracts"

host = mongo_uri
port = 27017

# Specify the required fields using dot notation
field_names = ["all_data","token_contracts"]
reader = SimpleMongoReader(host, port)

documents = reader.load_data(
    db_name, collection_name, field_names
)


async def ai_insight():
   
    try:
         
        prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n
            You are a crypto advisor and expert researcher tasked with gathering information for a daily report.  
            Identify unusual token patterns, price, and volume trends. Provide actionable insights in markdown format.

            format:
            Example: “Hello! I noticed an unusual surge in mentions of token XYZ, which correlates with a 20% volume increase in the past 24 hours. This token might be worth your attention!”
            Example: “Token ABC is showing an upward trend in mentions and liquidity. Based on past patterns, similar tokens experienced a 15%-30% appreciation within 48 hours.”
            (please Involve link related in)
            Write differently every time.

            write in markdown format within 500 characters.
            """
       
        # vector_store = FaissVectorStore.from_documents(documents)
        # index = SummaryIndex.from_vector_store(vector_store)   
        index = SummaryIndex.from_documents(documents)
        query_engine = index.as_query_engine(llm=llm, streaming=True, similarity_top_k=5)  # Pass the LLM to the query engine

        print("starting query...",query_engine)
        start_time = datetime.now()
        
        response = query_engine.query(prompt)  # Ensure this is awaited

        # Measure response time
        end_time = datetime.now()
        print(f"Query response received in {end_time - start_time} seconds.")
        # print(f"Querying for-----------------------: {query_text}")
        print(f"Query response received.-----------:{response}")
        return response
       
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing your request."

# Usage example
# asyncio.run(chat_bot("What is the highest token price change in the last 24 hours?"))
asyncio.run(ai_insight())   
