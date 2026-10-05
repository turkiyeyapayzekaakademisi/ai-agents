"""
Bu uygulama Semantic Memory kullanan bir AI Agent oluşturur.

Amaç:
    Kalıcı bilgilerin yalnızca birebir anahtar ile değil,
    anlamsal benzerlik kullanılarak bulunmasını göstermek.

Embedding:
    Ollama üzerinde qwen3-embedding:0.6b modeli kullanılır.

Vector Database:
    Chroma kullanılır ve veriler data/semantic_memory klasöründe kalıcı tutulur.
"""

from pathlib import Path  # Vector database klasörünün yolunu oluşturmak için kullanılır.
from typing import TypedDict  # LangGraph state modelini oluşturmak için kullanılır.
from uuid import uuid4  # Semantic memory kayıtlarına benzersiz ID vermek için kullanılır.
from langchain_chroma import Chroma  # Semantic memory için Chroma vector database kullanmak için kullanılır.
from langchain_core.documents import Document  # Hafıza kayıtlarını document olarak saklamak için kullanılır.
from langchain_core.messages import HumanMessage, SystemMessage  # Qwen'e mesaj göndermek için kullanılır.
from langchain_ollama import ChatOllama, OllamaEmbeddings  # Qwen LLM ve embedding modellerini kullanmak için kullanılır.
from langgraph.graph import END, START, StateGraph  # Semantic memory workflow'unu oluşturmak için kullanılır.


MODEL = "qwen3:4b"  # Cevap üretmek için kullanılacak LLM modelini tanımlar.
EMBEDDING_MODEL = "qwen3-embedding:0.6b"  # Semantic search için kullanılacak embedding modelini tanımlar.
VECTOR_PATH = Path(__file__).resolve().parent / "data" / "semantic_memory"  # Kalıcı Chroma database klasörünü tanımlar.


class SemanticState(TypedDict):  # Semantic memory graph state yapısını tanımlar.
    user_input: str  # Kullanıcının mevcut mesajını tutar.
    semantic_memories: list[str]  # Sorguya anlamsal olarak en yakın memory kayıtlarını tutar.
    memory_saved: bool  # Bu turda yeni semantic memory kaydedilip kaydedilmediğini tutar.
    response: str  # Agent'ın son cevabını tutar.


llm = ChatOllama(model=MODEL, temperature=0)  # Qwen3:4B LLM modelini oluşturur.
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)  # Qwen3 embedding modelini oluşturur.
vector_store = Chroma(collection_name="semantic_memory", embedding_function=embeddings, persist_directory=str(VECTOR_PATH))  # Kalıcı Chroma semantic memory database'ini oluşturur.


def semantic_memory_node(state: SemanticState) -> dict:  # Semantic memory yazma ve retrieval işlemlerini yapan node'u tanımlar.
    print("\n[NODE] semantic_memory")  # Eğitim sırasında semantic memory node'unun çalıştığını gösterir.
    user_input = state["user_input"]  # Kullanıcının mevcut mesajını state'ten alır.
    memory_saved = False  # Başlangıçta yeni memory eklenmediğini belirtir.

    if user_input.lower().startswith("hatırla:"):  # Kullanıcının yeni semantic memory kaydetmek isteyip istemediğini kontrol eder.
        memory = user_input.split(":", 1)[1].strip()  # Kaydedilecek hafıza metnini çıkarır.
        document = Document(page_content=memory, metadata={"type": "semantic_memory"})  # Hafızayı Chroma'ya uygun Document nesnesine dönüştürür.
        vector_store.add_documents(documents=[document], ids=[str(uuid4())])  # Memory'yi embedding'e çevirerek Chroma'ya kaydeder.
        memory_saved = True  # Yeni semantic memory kaydedildiğini belirtir.

    results = vector_store.similarity_search(user_input, k=3)  # Kullanıcı mesajına anlamsal olarak en yakın üç memory kaydını getirir.
    semantic_memories = [document.page_content for document in results]  # Bulunan document'ların metin içeriklerini listeye dönüştürür.
    return {"semantic_memories": semantic_memories, "memory_saved": memory_saved}  # Bulunan memory'leri state'e yazar.


def agent_node(state: SemanticState) -> dict:  # Semantic memory sonuçlarını kullanarak cevap oluşturan agent node'unu tanımlar.
    print("[NODE] agent")  # Eğitim sırasında agent node'unun çalıştığını gösterir.
    memory_text = "\n".join(f"- {memory}" for memory in state["semantic_memories"]) or "İlgili semantic memory bulunamadı."  # Retrieved memory'leri prompt formatına dönüştürür.
    system_prompt = f"""Sen semantic memory kullanan yardımcı bir AI agentsın.

Kullanıcının mevcut sorusuyla anlamsal olarak ilişkili hafıza kayıtları:
{memory_text}

Bu hafıza kayıtlarını yalnızca soruyla ilgili olduklarında kullan.
Tool veya memory sonuçlarında bulunmayan kişisel bilgileri üretme.
Türkçe cevap ver."""  # Retrieved semantic memory'leri modele veren system prompt oluşturur.
    response = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=state["user_input"])])  # Qwen'i semantic memory context'i ile çalıştırır.
    return {"response": response.content}  # Model cevabını state'e yazar.


builder = StateGraph(SemanticState)  # Semantic memory workflow'u için graph oluşturur.
builder.add_node("semantic_memory", semantic_memory_node)  # Semantic search node'unu graph'a ekler.
builder.add_node("agent", agent_node)  # Qwen agent node'unu graph'a ekler.
builder.add_edge(START, "semantic_memory")  # Graph'ın önce semantic memory'yi aramasını sağlar.
builder.add_edge("semantic_memory", "agent")  # Retrieved memory'lerden sonra modeli çalıştırır.
builder.add_edge("agent", END)  # Model cevabından sonra graph'ı sonlandırır.
graph = builder.compile()  # Graph'ı çalıştırılabilir hale getirir.


def main() -> None:  # Semantic memory uygulamasını terminalde çalıştırır.
    print("Çıkmak için 'exit' yazın.\n")  # Çıkış komutunu kullanıcıya gösterir.

    while True:  # Çok turlu terminal kullanımını sağlar.
        user_input = input("Kullanıcı: ")  # Kullanıcı mesajını alır.

        if user_input.lower() == "exit":  # Çıkış komutunu kontrol eder.
            break  # Programı sonlandırır.

        initial_state = {"user_input": user_input, "semantic_memories": [], "memory_saved": False, "response": ""}  # Semantic graph'ın başlangıç state'ini oluşturur.
        result = graph.invoke(initial_state)  # Semantic memory graph'ını çalıştırır.

        print("\nBulunan Semantic Memory:")  # Retrieval sonuçlarının gösterileceğini belirtir.

        for memory in result["semantic_memories"]:  # Bulunan her semantic memory üzerinde döner.
            print("-", memory)  # Memory içeriğini terminalde gösterir.

        print("\nAgent:", result["response"], "\n")  # Agent'ın cevabını gösterir.


if __name__ == "__main__":  # Dosyanın doğrudan çalıştırılıp çalıştırılmadığını kontrol eder.
    main()  # Semantic memory uygulamasını başlatır.