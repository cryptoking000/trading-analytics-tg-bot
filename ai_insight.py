from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from llama_index.llms.openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio
# from llama_index.vector_stores import FaissVectorStore
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

documents = reader.load_data(
    db_name, collection_name, field_names
)


async def ai_insight():
   
    try:
         
        prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n
            As your dedicated crypto market analyst, I analyze token patterns, price movements, and market dynamics to provide actionable insights.
    
            Focus Areas:
            1. Token Mention Patterns & Volume Correlations
            2. Price Action Analysis
            3. Social Sentiment & Market Momentum
            4. Risk Assessment & Opportunities

            Expected Output Format:
            • "Alert: Token XYZ shows a significant correlation between mention frequency and price action. Recent data shows {mention_count} mentions in the last {time_period}, coinciding with a {percentage}% volume surge."
    
            • "Market Intel: token_name (contract_address) demonstrates unusual social momentum. Historical data suggests tokens with similar patterns have shown {percentage}% price movement within {timeframe}."

            Key Deliverables:
            - Token Name & Contract Address
            - Mention Frequency & Timing
            - Volume & Price Analytics
            - Social Media Presence (X, Telegram, Discord)
            - Risk Factors & Growth Indicators
            - Comparative Historical Analysis
    
            Please provide insights in Markdown format, limited to 500 characters, with verifiable data points and actionable conclusions.
            """           
       
        # vector_store = FaissVectorStore.from_documents(documents)
        # index = SummaryIndex.from_vector_store(vector_store)   
        index = SummaryIndex.from_documents(documents)
        query_engine = index.as_query_engine(llm=llm, streaming=True)  # Pass the LLM to the query engine

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
