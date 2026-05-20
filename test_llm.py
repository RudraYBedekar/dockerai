import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

os.environ["OPENAI_API_KEY"] = "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"
os.environ["OPENAI_API_BASE"] = "https://integrate.api.nvidia.com/v1"

try:
    llm = ChatOpenAI(model="meta/llama-3.1-70b-instruct")
    res = llm.invoke("hello")
    print(res)
except Exception as e:
    print("Error:", e)
