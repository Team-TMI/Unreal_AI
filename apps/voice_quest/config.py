from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

DB_PARAMS={
    "persist_directory": "./data/chroma_ver3",
    "embedding_function" : OpenAIEmbeddings(),
    "collection_name": "openai"
}