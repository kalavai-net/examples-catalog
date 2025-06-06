import requests

from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings

from rag_agent.env import (
    API_BASE_URL,
    API_KEY,
    LLM_MODEL,
    EMBEDDING_MODEL,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP
)


def chat_request(messages):
    response = requests.post(
        f"{API_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model":  LLM_MODEL,
            "messages": messages
        }
    )
    output = response.json()["choices"][0]["message"]["content"]
    return output

def generate_index(folder):
    documents = SimpleDirectoryReader(folder).load_data()
    Settings.chunk_size = DEFAULT_CHUNK_SIZE
    Settings.chunk_overlap = DEFAULT_CHUNK_OVERLAP
    index = VectorStoreIndex.from_documents(
        documents=documents,
        embed_model=OpenAILikeEmbedding(
            model_name=EMBEDDING_MODEL,
            api_base=API_BASE_URL,
            api_key=API_KEY,
            embed_batch_size=100,
            max_retries=100
        )
    )
    return index