"""
Settings file for testing database_handler, it should not have an impact on server.py
"""

import os
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

# SETUP EMBEDDING FUNCTIONS #
# these items should NOT be used in other scripts directly
# uses SentenceTransformers all-MiniLM-L6-v2 model
default_embedding = embedding_functions.DefaultEmbeddingFunction() 
openai_embedding = embedding_functions.OpenAIEmbeddingFunction(
    api_key = openai_api_key,
    model_name = "text-embedding-3-small" # default is text-embedding-ada-002
)

# CONFIGURATION #
# these items can be used directly in other scripts
# name of collection in the database
PATH_TO_DATA = "./db"
MAIN_COLLECTION_NAME = "extracted_json"
EMBEDDING_FUNCTION = openai_embedding
