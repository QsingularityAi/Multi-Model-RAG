from langchain_community.chat_models import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

def get_multimodal_llm():
    # Replace with your actual multimodal LLM configuration (e.g., OpenAI API)
    model = ChatOpenAI(temperature=0, model="gpt-4-vision-preview", max_tokens=1024)
    return model
