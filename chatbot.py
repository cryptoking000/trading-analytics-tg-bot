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
documents = None  # Initialize documents variable

async def chat_bot(input_message):
    global documents  # Use global variable to store documents
    try:
        if documents is None:  # Check if documents have already been loaded
            # Create a MongoDB reader and load data
            reader = SimpleMongoReader(host, port)

            print("Loading data from MongoDB...")
            documents = await reader.load_data(
                db_name, collection_name, field_names
            )
            print(f"Loaded {len(documents)} documents.")

            if not documents:
                print("No documents found.")
                return "No data available."

        # Use documents without reading again
        index = SummaryIndex.from_documents(documents)
        query_engine = index.as_query_engine(llm)  # Pass the LLM to the query engine

        query_text = input_message
        print(f"Querying for: {query_text}")
        response = await query_engine.query(query_text)  # Use await here

        print("Query response received.")
        print(response)
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing your request."