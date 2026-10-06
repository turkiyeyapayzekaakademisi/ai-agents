"""
Bu dosyada FAQ Agent tarafından kullanılan iki RAG tool bulunur.

search_general_faq:
    Genel müşteri sorularını general FAISS database içerisinde arar.

search_technical_faq:
    Teknik soruları technical FAISS database içerisinde arar.
"""

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool

from config import embeddings


BASE_PATH = Path(__file__).resolve().parent.parent
VECTOR_PATH = BASE_PATH / "vector_db"


general_db = FAISS.load_local(
    str(VECTOR_PATH / "general_faq"),
    embeddings,
    allow_dangerous_deserialization=True
)

technical_db = FAISS.load_local(
    str(VECTOR_PATH / "technical_faq"),
    embeddings,
    allow_dangerous_deserialization=True
)


@tool
def search_general_faq(query: str) -> str:
    """KDV, kargo ücreti, iade ve ödeme gibi genel müşteri sorularını araştırır."""

    print(f"\n[TOOL] search_general_faq({query})")

    results = general_db.similarity_search(query, k=2)

    return "\n\n".join(
        document.page_content
        for document in results
    )


@tool
def search_technical_faq(query: str) -> str:
    """Şifre, giriş, API ve uygulama gibi teknik müşteri sorularını araştırır."""

    print(f"\n[TOOL] search_technical_faq({query})")

    results = technical_db.similarity_search(query, k=2)

    return "\n\n".join(
        document.page_content
        for document in results
    )