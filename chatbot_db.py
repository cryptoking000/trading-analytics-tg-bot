from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core import SummaryIndex
from datetime import datetime
from llama_index.readers.mongodb import SimpleMongoReader
import os
from dotenv import load_dotenv
# from llama_index.vector_stores import FaissVectorStore
load_dotenv()
llm = OpenAI(
    model="gpt-4o-mini",  # Using standard gpt-4o-mini model
    api_key=os.getenv("OPENAI_API_KEY"),
    max_output_tokens=500,
    temperature=0.8  # Add temperature for better response variety
)

mongo_uri = os.getenv("MONGO_URI")
db_name = "telegram_bot_db"
collection_name = "token_contracts_analytics_data"

host = mongo_uri
port = 27017
field_names = [
    "token_contracts",
    "mentioned_lastdate",
    "total_mentions",
    "daily_mentions",
    "token_analytics_data"
]

reader = SimpleMongoReader(host, port)

async def chatbot_db(input_message):
    try:
        documents = reader.load_data(
                    db_name, collection_name, field_names
        )
        print("📖Documents loaded successfully. ai_insight")
        
        index = SummaryIndex.from_documents(documents,)
        prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n
                    As a professional cryptocurrency advisor and investment expert, 
                    please answer the following question concisely: {input_message}. 
                    Don't provide real-time data, just answer the question in the my database.
                    """      

        # chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
        start_time = datetime.now()
        chat_engine = index.as_chat_engine(chat_mode="react", llm=llm, verbose=True)
        response = chat_engine.chat(prompt)
        end_time = datetime.now()
        print(f"Query response received in {end_time - start_time} seconds.")
        print("🤔",response)
        return str(response)
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing your request."
    