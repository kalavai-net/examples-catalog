"""
This file contains the credentials and configurations for CoGen AI inference.

To get a free account on CoGen AI, visit: https://cogenai.kalavai.net
"""

API_BASE_URL = "https://api.cogenai.kalavai.net/v1"
API_KEY = "" # <-- TODO: add your CoGen AI API key here
LLM_MODEL = "qwen-qwen2-5-7b-instruct-awq"
EMBEDDING_MODEL = "qwen-qwen3-embedding-0-6b" # "intfloat-multilingual-e5-large-instruct" #"qwen-qwen3-embedding-0-6b"
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 100