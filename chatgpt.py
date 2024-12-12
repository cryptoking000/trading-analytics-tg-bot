import logging
import sys
import os
from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from IPython.display import Markdown, display
from dotenv import load_dotenv

from llama_index.llms.openai import OpenAI

load_dotenv()  # Load environment variables from .env file
llm = OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("API_KEY"))  # Use environment variable for API key
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# Define MongoDB connection parameters
mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://andyblake:crs19981106@messagescluster.ci599.mongodb.net/?retryWrites=true&w=majority&appName=MessagesCluster")
db_name = "telegram_bot_db"
collection_name = "token_data"

host = mongo_uri
port = 27017

# Specify the required fields using dot notation
field_names = [
    "data.schemaVersion",
    "data.pairs.chainId",
    "data.pairs.dexId",
    "data.pairs.url",
    "data.pairs.pairAddress",
    "data.pairs.baseToken.name",
    "data.pairs.baseToken.symbol",
    "data.pairs.quoteToken.name",
    "data.pairs.quoteToken.symbol",
    "data.pairs.priceNative",
    "data.pairs.priceUsd",
    "data.pairs.priceChange.h24",
    "data.pairs.liquidity.usd",
]

# Create a MongoDB reader and load data
reader = SimpleMongoReader(host, port)

documents = reader.load_data(
    db_name, collection_name, field_names
)


# Initialize settings and query engine
index = SummaryIndex.from_documents(documents)
query_engine = index.as_query_engine(llm=llm)  # Pass the LLM to the query engine

try:
    # Perform the query
    query_text = "what token has the highest price change in the last 24 hours"
    response = query_engine.query(query_text)

    if not response:  # Check if response is empty or None
        logging.error("Query returned no response.")
        sys.exit("Exiting due to query failure.")

    # Format and display the response
    formatted_response = f"<b>{response}</b>"
    print(formatted_response)
    display(Markdown(formatted_response))

except Exception as e:
    logging.error(f"An error occurred: {e}")
    sys.exit("Exiting due to an error.")
