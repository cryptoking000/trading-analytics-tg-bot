from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from llama_index.llms.openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler

from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
import tiktoken
load_dotenv()

llm = OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), max_output_tokens=500)  # Use environment variable for API key
mongo_uri = os.getenv("MONGO_URI")
db_name = "telegram_bot_db"
collection_name = "token_contracts_analytics_data"

host = mongo_uri
port = 27017

# Specify the required fields using dot notation
field_names = ["all_token_data","num_times_all_mentioned","last_mention_date"]
reader = SimpleMongoReader(host, port)

tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo").encode

# Create a TokenCountingHandler instance
token_counter = TokenCountingHandler(tokenizer=tokenizer, verbose=True)

# Set up the callback manager with the token counter
callback_manager = CallbackManager([token_counter])
# Load documents (adjust the path as necessary)


documents = reader.load_data(
            db_name, collection_name, field_names
)



async def ai_insight():

    try:
        
    
        prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n
          You are a crypto advisor and professional researcher responsible for gathering information for daily reports.
            Identify unusual token patterns, price and volume trends. Provide actionable insights in Markdown format.

            Reference to Format:
            Example: "Hi! I've noticed an unusual spike in mentions of [token name], which is associated with a [percent]% increase in volume over the last [hours]. This token may be of interest to you!"
            Example: "[Token name] is trending upward in mentions and liquidity. Based on historical patterns, similar tokens have seen a [percent]%-[percent]% increase in the last [hours]."
            (Include relevant links like x, telegram and origin)
            must write differently every time.
            Use data like mention time and number.
            Write in Markdown format, with in 500 characters.
            """
             

        index = SummaryIndex.from_documents(documents, callback_manager=callback_manager)
        query_engine = index.as_query_engine(llm=llm, streaming=True)  # Pass the LLM to the query engine

        print("starting query...",query_engine)
        start_time = datetime.now()

        response = query_engine.query(prompt)  # Ensure this is awaited

        # Get performance metrics
       
        # Print token counts
        print("Embedding Tokens:", token_counter.total_embedding_token_count)
        print("LLM Prompt Tokens:", token_counter.prompt_llm_token_count)
        print("LLM Completion Tokens:", token_counter.completion_llm_token_count)
        print("Total LLM Token Count:", token_counter.total_llm_token_count)

        # Optionally reset counts if needed
        token_counter.reset_counts()

        # Measure response time
        end_time = datetime.now()
        print(f"Query response received in {end_time - start_time} seconds.")
        print(f"Query response received.-----------:{response}")
        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing your request."

# Usage example
asyncio.run(ai_insight())