import os
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.Client()
collection = client.get_or_create_collection(name="healthcare_memory")

embedding_function = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

def add_to_memory(user_id: str, text: str):
    collection.add(documents=[text], ids=[user_id + "_" + str(hash(text))])

def retrieve_relevant_context(query: str, top_k: int = 3):
    results = collection.query(query_texts=[query], n_results=top_k)
    if results["documents"]:
        return " ".join([doc for docs in results["documents"] for doc in docs])
    return ""
