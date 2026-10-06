"""
Bu dosya general_faq.json ve technical_faq.json verilerini okur,
Qwen3 Embedding modeli ile embedding oluşturur ve
iki ayrı FAISS vector database oluşturur.
"""

import json
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config import embeddings


BASE_PATH = Path(__file__).resolve().parent
DATA_PATH = BASE_PATH / "data"
VECTOR_PATH = BASE_PATH / "vector_db"


def load_documents(file_path: Path) -> list[Document]:
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    documents = []

    for item in data:
        content = f"Soru: {item['question']}\nCevap: {item['answer']}"
        documents.append(Document(page_content=content))

    return documents


def create_vector_db(json_name: str, output_name: str) -> None:
    documents = load_documents(DATA_PATH / json_name)
    vector_db = FAISS.from_documents(documents, embeddings)

    output_path = VECTOR_PATH / output_name
    output_path.mkdir(parents=True, exist_ok=True)

    vector_db.save_local(str(output_path))

    print(f"[OK] {output_name} oluşturuldu.")


def main() -> None:
    create_vector_db("general_faq.json", "general_faq")
    create_vector_db("technical_faq.json", "technical_faq")


if __name__ == "__main__":
    main()