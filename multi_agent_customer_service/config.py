"""
Bu dosyada projede kullanılacak LLM ve embedding modelleri tanımlanır.
"""

from langchain_ollama import ChatOllama, OllamaEmbeddings

LLM_MODEL = "qwen3:4b"
EMBEDDING_MODEL = "qwen3-embedding:0.6b"

llm = ChatOllama(model=LLM_MODEL, temperature=0)
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)