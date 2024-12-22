from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from IPython.display import Markdown, display
from llama_index.llms.openai import OpenAI
# from chatbot_tavily import tavily_search
from llama_index.core import Document
import asyncio
from datetime import datetime
import os
import json
from dotenv import load_dotenv
load_dotenv()

async def chat_bot(input_message):
    try:

        chat_engine = SimpleChatEngine.from_defaults()
        prompt = f"""Today's date is {datetime.now().strftime('%d/%m/%Y')}.\n
            You are a crypto advisor and expert researcher tasked with gathering information for a daily report.   Your current objective is to gather documents about : "https://dexscreener.com".\n
            you should tell very short and comprehensive answer to the following question: {input_message}
            write in markdown format within 500 words.
            """
        
        print("Documents loaded successfully.")
        response = chat_engine.chat(prompt )
        
        print("Query response received.----------------------")
        print(response)
        return response
       
    except Exception as e:
        print(f"An error occurred: {e}")
        return "An error occurred while processing your request."
