import openai
import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.memory import ChatMemoryBuffer

openai.api_key = os.getenv("OPENAI_API_KEY")
data = SimpleDirectoryReader(input_dir="./data/paul_graham/").load_data()
index = VectorStoreIndex.from_documents(data)

memory = ChatMemoryBuffer.from_defaults(token_limit=1500)

chat_engine = index.as_chat_engine(
    chat_mode="context",
    memory=memory,
    system_prompt=(
        "You are a chatbot, able to have normal interactions, as well as talk"
        " about an essay discussing Paul Grahams life."
    ),
)

response = chat_engine.chat("Hello!")
print(response)



