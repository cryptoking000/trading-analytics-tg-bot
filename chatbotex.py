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

# llm = OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"), max_output_tokens=500)  # Use environment variable for API key
mongo_uri = os.getenv("MONGO_URI")
db_name = "telegram_bot_db"
collection_name = "token_contracts_analytics_data"

host = mongo_uri
port = 27017

print(f"Connecting to MongoDB at {host}:{port}")
print(f"Database: {db_name}, Collection: {collection_name}")
print(f"time noww: {datetime.now()}")
# Specify the required fields using dot notation
field_names = ["token_contracts","mentioned_lastdate","total_mentions","daily_mentions","token_analytics_data"]

reader = SimpleMongoReader(host, port)

print("Loading data from MongoDB...")
print(f"time noww: {datetime.now()}")
documents = reader.load_data(
    db_name, collection_name, field_names
)

print(f"Loaded {len(documents)} documents")
print(f"time noww: {datetime.now()}")

llm = OpenAI(model="gpt-4o-mini", temperature=0)
Settings.llm = llm
print("Creating vector index...")
print(f"time noww: {datetime.now()}")
# index = VectorStoreIndex.from_documents(documents)
index = SummaryIndex.from_documents(documents)
print("Creating chat engine...")

print(f"time noww: {datetime.now()}")
documents = SimpleMongoReader(host, port).load_data(db_name, collection_name, field_names)
index = VectorStoreIndex.from_documents(documents)
print(f"time noww: {datetime.now()}")
chat_engine = index.as_chat_engine(chat_mode="react", llm=llm, verbose=True)
# chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
print(f"time noww: {datetime.now()}")
response = chat_engine.chat("What token is top price in the last 24 hours?")


print("\nResponse:")
print(response)