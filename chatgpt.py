import logging
import sys
<<<<<<< HEAD
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
=======
import json

from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from IPython.display import Markdown, display
import os
from llama_index.core.indices.struct_store import JSONQueryEngine
from llama_index.core.service_context import ServiceContext
>>>>>>> 273c5851b993460ca188f04709ea221f0ff2e770

# Define MongoDB connection parameters
mongo_uri = os.getenv("MONGO_URI", "mongodb+srv://andyblake:crs19981106@messagescluster.ci599.mongodb.net/?retryWrites=true&w=majority&appName=MessagesCluster")
db_name = "telegram_bot_db"
collection_name = "token_data"
<<<<<<< HEAD

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
=======
host = mongo_uri
port = 27017

# Define query parameters
query_dict = {}
field_names = ["data"]

# Create a MongoDB reader and load data
reader = SimpleMongoReader(host, port)
documents = reader.load_data(db_name, collection_name, field_names, query_dict=query_dict)

# Ensure documents are not empty before proceeding
if not documents:
    logging.error("No documents found in the collection.")
    sys.exit("Exiting due to lack of data.")

# Create a SummaryIndex from the documents
index = SummaryIndex.from_documents(documents)

# Create a ServiceContext
service_context = ServiceContext()

# Create a JSONQueryEngine and perform a query
json_value = json.loads(documents) if isinstance(documents, str) else documents
json_schema = {
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "_id": {
      "type": "object",
      "properties": {
        "$oid": { "type": "string" }
      },
      "required": ["$oid"]
    },
    "data": {
      "type": "object",
      "properties": {
        "schemaVersion": { "type": "string" },
        "pairs": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "chainId": { "type": "string" },
              "dexId": { "type": "string" },
              "url": { "type": "string", "format": "uri" },
              "pairAddress": { "type": "string" },
              "labels": {
                "type": "array",
                "items": { "type": "string" }
              },
              "baseToken": {
                "type": "object",
                "properties": {
                  "address": { "type": "string" },
                  "name": { "type": "string" },
                  "symbol": { "type": "string" }
                },
                "required": ["address", "name", "symbol"]
              },
              "quoteToken": {
                "type": "object",
                "properties": {
                  "address": { "type": "string" },
                  "name": { "type": "string" },
                  "symbol": { "type": "string" }
                },
                "required": ["address", "name", "symbol"]
              },
              "priceNative": { "type": "string" },
              "priceUsd": { "type": "string" },
              "txns": {
                "type": "object",
                "properties": {
                  "m5": {
                    "type": "object",
                    "properties": {
                      "buys": { "type": "object", "properties": { "$numberInt": { "type": "string" } }, "required": ["$numberInt"] },
                      "sells": { "type": "object", "properties": { "$numberInt": { "type": "string" } }, "required": ["$numberInt"] }
                    },
                    "required": ["buys", "sells"]
                  },
                  "h1": {
                    "type": "object",
                    "properties": {
                      "buys": { "type": "object", "properties": { "$numberInt": { "type": "string" } }, "required": ["$numberInt"] },
                      "sells": { "type": "object", "properties": { "$numberInt": { "type": "string" } }, "required": ["$numberInt"] }
                    },
                    "required": ["buys", "sells"]
                  },
                  "h6": {
                    "type": "object",
                    "properties": {
                      "buys": { "type": "object", "properties": { "$numberInt": { "type": "string" } }, "required": ["$numberInt"] },
                      "sells": { "type": "object", "properties": { "$numberInt": { "type": "string" } }, "required": ["$numberInt"] }
                    },
                    "required": ["buys", "sells"]
                  },
                  "h24": {
                    "type": "object",
                    "properties": {
                      "buys": { "type": "object", "properties": { "$numberInt": { "type": "string" } }, "required": ["$numberInt"] },
                      "sells": { "type": "object", "properties": { "$numberInt": { "type": "string" } }, "required": ["$numberInt"] }
                    },
                    "required": ["buys", "sells"]
                  }
                },
                "required": ["m5", "h1", "h6", "h24"]
              },
              "volume": {
                "type": "object",
                "properties": {
                  "h24": { "type": "object", "properties": { "$numberDouble": { "type": "string" } }, "required": ["$numberDouble"] },
                  "h6": { "type": "object", "properties": { "$numberDouble": { "type": "string" } }, "required": ["$numberDouble"] },
                  "h1": { "type": "object", "properties": { "$numberDouble": { "type": "string" } }, "required": ["$numberDouble"] },
                  "m5": { "type": "object", "properties": { "$numberInt": { "type": "string" } }, "required": ["$numberInt"] }
                },
                "required": ["h24", "h6", "h1", "m5"]
              },
              "priceChange": {
                "type": "object",
                "properties": {
                  "m5": { "type": "object", "properties": { "$numberDouble": { "type": "string" } }, "required": ["$numberDouble"] },
                  "h1": { "type": "object", "properties": { "$numberDouble": { "type": "string" } }, "required": ["$numberDouble"] },
                  "h6": { "type": "object", "properties": { "$numberDouble": { "type": "string" } }, "required": ["$numberDouble"] },
                  "h24": { "type": "object", "properties": { "$numberDouble": { "type": "string" } }, "required": ["$numberDouble"] }
                },
                "required": ["m5", "h1", "h6", "h24"]
              },
              "liquidity": {
                "type": "object",
                "properties": {
                  "usd": { "type": "object", "properties": { "$numberDouble": { "type": "string" } }, "required": ["$numberDouble"] },
                  "base": { "type": "object", "properties": { "$numberInt": { "type": "string" } }, "required": ["$numberInt"] },
                  "quote": { "type": "object", "properties": { "$numberDouble": { "type": "string" } }, "required": ["$numberDouble"] }
                },
                "required": ["usd", "base", "quote"]
              },
              "fdv": {
                "type": "object",
                "properties": {
                  "$numberInt": { "type": "string" }
                },
                "required": ["$numberInt"]
              },
              "marketCap": {
                "type": "object",
                "properties": {
                  "$numberInt": { "type": "string" }
                },
                "required": ["$numberInt"]
              },
              "pairCreatedAt": {
                "type": "object",
                "properties": {
                  "$numberLong": { "type": "string" }
                },
                "required": ["$numberLong"]
              }
            },
            "required": [
              "chainId",
              "dexId",
              "url",
              "pairAddress",
              "labels",
              "baseToken",
              "quoteToken",
              "priceNative",
              "priceUsd",
              "txns",
              "volume",
              "priceChange",
              "liquidity",
              "fdv",
              "marketCap"
            ]
          }
        }
      },
      "required": ["schemaVersion", "pairs"]
    }
  },
  "required": ["_id", "data"]
}

query_engine = JSONQueryEngine(json_value, json_schema, service_context)

# Perform the query and handle the response
query_text = "what token has the highest price change in the last 24 hours"  # Replace with actual query text
response = query_engine.query(query_text)

if response is None:
    logging.error("Query returned no response.")
    sys.exit("Exiting due to query failure.")

# Format and display the response
formatted_response = f"<b>{response}</b>"
print(formatted_response)
display(Markdown(formatted_response))
>>>>>>> 273c5851b993460ca188f04709ea221f0ff2e770
