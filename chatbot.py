from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from IPython.display import Markdown, display
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4o-mini", api_key="apikey")  # Use environment variable for API key

mongo_uri = "mongodb+srv://andyblake:crs19981106@messagescluster.ci599.mongodb.net/?retryWrites=true&w=majority&appName=MessagesCluster"
db_name = "telegram_bot_db"
collection_name = "token_data"

host = mongo_uri
port = 27017

# Specify the required fields using dot notation
field_names = ["data"]

async def chat_bot(input_message):
        
    # Create a MongoDB reader and load data
    reader = SimpleMongoReader(host, port)

    print("Loading data from MongoDB...")
    documents = reader.load_data(
        db_name, collection_name, field_names
    )
    print(f"Loaded {len(documents)} documents.")

    index = SummaryIndex.from_documents(documents)
    query_engine = index.as_query_engine(llm=llm)  # Pass the LLM to the query engine

    query_text = input_message
    print(f"Querying for: {query_text}")
    response = query_engine.query(query_text)

    print("Query response received.")
    print(response)