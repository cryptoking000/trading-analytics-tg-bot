from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core import SummaryIndex

from llama_index.readers.mongodb import SimpleMongoReader
import os
from dotenv import load_dotenv
# from llama_index.vector_stores import FaissVectorStore
load_dotenv()

# llm = OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"), max_output_tokens=500)  # Use environment variable for API key
mongo_uri = os.getenv("MONGO_URI")
db_name = "telegram_bot_db"
collection_name = "token_contracts"

host = mongo_uri
port = 27017

print(f"Connecting to MongoDB at {host}:{port}")
print(f"Database: {db_name}, Collection: {collection_name}")

# Specify the required fields using dot notation
field_names = ["all_data","token_contracts"]
reader = SimpleMongoReader(host, port)

print("Loading data from MongoDB...")
documents = reader.load_data(
    db_name, collection_name, field_names
)

print(f"Loaded {len(documents)} documents")

llm = OpenAI(model="gpt-3.5-turbo", temperature=0)
Settings.llm = llm
print("Creating vector index...")
# index = VectorStoreIndex.from_documents(documents)
index = SummaryIndex.from_documents(documents)
print("Creating chat engine...")
# from llama_index.core.memory import ChatMemoryBuffer

# memory = ChatMemoryBuffer.from_defaults(token_limit=3900)

# chat_engine = index.as_chat_engine(
#     chat_mode="condense_plus_context",
#     memory=memory,
#     llm=llm,
#     context_prompt=(
#         "You are a chatbot, able to have normal interactions, as well as talk"
#         " about an essay discussing Paul Grahams life."
#         "Here are the relevant documents for the context:\n"
#         "{context_str}"
#         "\nInstruction: Use the previous chat history, or the context above, to interact and help the user."
#     ),
#     verbose=False,
# )
# print("Sending query to chat engine...")
# response = chat_engine.stream_chat("What token is top price in the last 24 hours?")

# for token in response.response_gen:
#     print(token, end="")
documents = SimpleMongoReader(host, port).load_data(db_name, collection_name, field_names)
index = VectorStoreIndex.from_documents(documents)
chat_engine = index.as_chat_engine(chat_mode="react", llm=llm, verbose=True)
# chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
response = chat_engine.chat("What token is top price in the last 24 hours?")


print("\nResponse:")
print(response)