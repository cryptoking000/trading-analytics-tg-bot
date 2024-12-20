from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from IPython.display import Markdown, display
from llama_index.llms.openai import OpenAI
# from chatbot_tavily import tavily_search
from llama_index.core import Document
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

llm = OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))  # Use environment variable for API key

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
            Use AI algorithms to detect unusual patterns, such as sudden increases in token mentions across multiple groups.
            Correlate token mentions with price and volume movements to identify potential opportunities.
            Provide a sentence like the following:
            Example: “Hello! I noticed an unusual surge in mentions of token XYZ, which correlates with a 20% volume increase in the past 24 hours. This token might be worth your attention!”
            Example: “Token ABC is showing an upward trend in mentions and liquidity. Based on past patterns, similar tokens experienced a 15%-30% appreciation within 48 hours.”
            (please Involve link related in)
            Write differently every time.

            write in markdown format within 500 characters.
            """
        # print("Generated prompt for TavilyClient:")
     
        # text_list = await tavily_search(input_message)
        # # if not documents:
        # #     print("error______")
        # #     return "No documents found for the given input."
       
        # documents = [Document(text=t) for t in text_list]
        index = SummaryIndex.from_documents(documents)
        query_engine = index.as_query_engine(llm)  # Pass the LLM to the query engine

        query_text = prompt
        response =  query_engine.query(query_text)  # Use await here

        print(f"Querying for-----------------------: {query_text}")
        print(f"Query response received.-----------:{response}")
        return response
       
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing your request."

# Usage example
# asyncio.run(chat_bot("What is the highest token price change in the last 24 hours?"))
