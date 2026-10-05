"""
Bu uygulama State, Conversation Memory, Long-Term Memory ve Semantic Memory
kavramlarını tek bir LangGraph AI Agent içerisinde birleştirir.

State:
    Graph içerisindeki mevcut çalışma verilerini taşır.

Conversation Memory:
    LangGraph InMemorySaver ve thread_id kullanılarak konuşma geçmişini korur.

Long-Term Memory:
    Kullanıcının açıkça kaydettiği bilgiler JSON dosyasında kalıcı tutulur.

Semantic Memory:
    Kalıcı bilgiler Qwen3 Embedding ve Chroma kullanılarak anlamsal olarak aranır.

Model:
    Ollama üzerinde çalışan qwen3:4b kullanılır.
"""

import json  # Long-term memory dosyasını okumak ve yazmak için kullanılır.
from pathlib import Path  # Memory dosyalarının yollarını oluşturmak için kullanılır.
from uuid import uuid4  # Semantic memory kayıtları için benzersiz kimlik oluşturmak için kullanılır.
from langchain_chroma import Chroma  # Semantic memory vector database'ini kullanmak için kullanılır.
from langchain_core.documents import Document  # Semantic memory kayıtlarını document olarak oluşturmak için kullanılır.
from langchain_core.messages import SystemMessage  # Agent'a system prompt göndermek için kullanılır.
from langchain_ollama import ChatOllama, OllamaEmbeddings  # Qwen LLM ve embedding modellerini kullanmak için kullanılır.
from langgraph.checkpoint.memory import InMemorySaver  # Conversation memory için thread state'ini RAM'de saklamak için kullanılır.
from langgraph.graph import END, START, MessagesState, StateGraph  # LangGraph stateful agent yapısını oluşturmak için kullanılır.


MODEL = "qwen3:4b"  # Agent'ın cevap üretmek için kullanacağı LLM modelini tanımlar.
EMBEDDING_MODEL = "qwen3-embedding:0.6b"  # Semantic memory için kullanılacak embedding modelini tanımlar.
BASE_PATH = Path(__file__).resolve().parent  # Projenin ana klasör yolunu oluşturur.
LONG_TERM_MEMORY_PATH = BASE_PATH / "data" / "long_term_memory.json"  # Kalıcı JSON memory dosyasının yolunu tanımlar.
VECTOR_PATH = BASE_PATH / "data" / "semantic_memory"  # Kalıcı Chroma vector store klasörünü tanımlar.


class AgentState(MessagesState):  # LangGraph MessagesState'i genişleterek özel state alanları ekler.
    long_term_memories: list[str]  # JSON içerisindeki kalıcı hafıza kayıtlarını tutar.
    semantic_memories: list[str]  # Kullanıcı sorusuna anlamsal olarak yakın memory kayıtlarını tutar.
    memory_saved: bool  # Bu turda yeni memory kaydedilip kaydedilmediğini tutar.


llm = ChatOllama(model=MODEL, temperature=0)  # Qwen3:4B modelini oluşturur.
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)  # Semantic search için Qwen3 embedding modelini oluşturur.
vector_store = Chroma(collection_name="semantic_memory", embedding_function=embeddings, persist_directory=str(VECTOR_PATH))  # Kalıcı semantic memory vector store oluşturur.
checkpointer = InMemorySaver()  # Conversation history'yi thread bazında RAM'de saklayan checkpointer oluşturur.


def load_long_term_memories() -> list[str]:  # JSON içerisindeki kalıcı memory kayıtlarını yükler.
    with LONG_TERM_MEMORY_PATH.open("r", encoding="utf-8") as file:  # Long-term memory dosyasını açar.
        data = json.load(file)  # JSON içeriğini Python nesnesine dönüştürür.
    return data.get("memories", [])  # Memory listesini döndürür.


def save_long_term_memory(memory: str) -> None:  # Yeni bilgiyi JSON long-term memory'ye kaydeder.
    memories = load_long_term_memories()  # Mevcut long-term memory kayıtlarını yükler.

    if memory not in memories:  # Bilginin daha önce kaydedilip kaydedilmediğini kontrol eder.
        memories.append(memory)  # Yeni bilgiyi memory listesine ekler.

    with LONG_TERM_MEMORY_PATH.open("w", encoding="utf-8") as file:  # JSON memory dosyasını yazma modunda açar.
        json.dump({"memories": memories}, file, ensure_ascii=False, indent=2)  # Güncellenmiş hafızayı kalıcı olarak kaydeder.


def memory_node(state: AgentState) -> dict:  # Long-term ve semantic memory işlemlerini gerçekleştiren graph node'unu tanımlar.
    print("\n[NODE] memory")  # Eğitim sırasında memory node'unun çalıştığını terminalde gösterir.
    last_message = state["messages"][-1].content  # Kullanıcının son mesajını conversation state'inden alır.
    memory_saved = False  # Başlangıçta yeni hafıza kaydedilmediğini belirtir.

    if last_message.lower().startswith("hatırla:"):  # Kullanıcının açıkça yeni bilgi kaydetmek isteyip istemediğini kontrol eder.
        memory = last_message.split(":", 1)[1].strip()  # "hatırla:" sonrasındaki bilgiyi çıkarır.
        save_long_term_memory(memory)  # Bilgiyi JSON long-term memory'ye kaydeder.
        document = Document(page_content=memory, metadata={"type": "semantic_memory"})  # Aynı bilgiyi semantic memory document'ına dönüştürür.
        vector_store.add_documents(documents=[document], ids=[str(uuid4())])  # Memory'yi embedding ile Chroma vector store'a kaydeder.
        memory_saved = True  # Bu turda memory kaydedildiğini belirtir.

    long_term_memories = load_long_term_memories()  # Bütün kalıcı memory kayıtlarını JSON dosyasından yükler.
    semantic_results = vector_store.similarity_search(last_message, k=3)  # Son kullanıcı mesajına anlamsal olarak en yakın üç memory kaydını getirir.
    semantic_memories = [document.page_content for document in semantic_results]  # Chroma sonuçlarını metin listesine dönüştürür.

    return {"long_term_memories": long_term_memories, "semantic_memories": semantic_memories, "memory_saved": memory_saved}  # Memory sonuçlarını LangGraph state'ine yazar.


def agent_node(state: AgentState) -> dict:  # Conversation history ve memory bilgilerini kullanarak cevap oluşturan node'u tanımlar.
    print("[NODE] agent")  # Eğitim sırasında agent node'unun çalıştığını gösterir.
    long_term_text = "\n".join(f"- {memory}" for memory in state["long_term_memories"]) or "Kayıtlı long-term memory bulunmuyor."  # Long-term memory'leri prompt metnine dönüştürür.
    semantic_text = "\n".join(f"- {memory}" for memory in state["semantic_memories"]) or "İlgili semantic memory bulunamadı."  # Semantic retrieval sonuçlarını prompt metnine dönüştürür.

    system_prompt = f"""Sen state ve memory kullanan kişisel bir AI agentsın.

LONG-TERM MEMORY:
{long_term_text}

MEVCUT SORUYLA İLGİLİ SEMANTIC MEMORY:
{semantic_text}

Kurallar:
- Conversation history içindeki önceki mesajları dikkate al.
- Long-term memory bilgilerini gerektiğinde kullan.
- Semantic memory sonuçlarından yalnızca mevcut soruyla ilgili olanları kullan.
- Memory'de bulunmayan kişisel bilgileri uydurma.
- Kullanıcı 'hatırla:' ile bilgi verdiyse bilgiyi kaydettiğini kısa şekilde belirt.
- Türkçe cevap ver."""  # Conversation, long-term ve semantic memory kullanım kurallarını tanımlar.

    response = llm.invoke([SystemMessage(content=system_prompt), *state["messages"]])  # Qwen'i system context ve bütün conversation history ile çalıştırır.
    return {"messages": [response]}  # Agent cevabını MessagesState'e ekler.


builder = StateGraph(AgentState)  # State ve memory kullanan LangGraph graph'ını oluşturur.
builder.add_node("memory", memory_node)  # Memory retrieval ve write node'unu graph'a ekler.
builder.add_node("agent", agent_node)  # Qwen agent node'unu graph'a ekler.
builder.add_edge(START, "memory")  # Her kullanıcı mesajında önce memory katmanını çalıştırır.
builder.add_edge("memory", "agent")  # Memory sonuçlarından sonra agent'ı çalıştırır.
builder.add_edge("agent", END)  # Agent cevabından sonra mevcut graph turunu sonlandırır.
graph = builder.compile(checkpointer=checkpointer)  # Graph'ı conversation memory sağlayan checkpointer ile derler.


def main() -> None:  # Final state + memory agent uygulamasını çalıştırır.
    thread_id = "conversation-1"  # Mevcut conversation session'ın kimliğini tanımlar.
    config = {"configurable": {"thread_id": thread_id}}  # LangGraph checkpointer için thread config oluşturur.
    print("Çıkmak için 'exit' yazın.\n")  # Kullanıcıya çıkış komutunu gösterir.

    while True:  # Çok turlu conversation döngüsünü başlatır.
        user_input = input("Kullanıcı: ")  # Kullanıcıdan yeni mesaj alır.

        if user_input.lower() == "exit":  # Çıkış komutunu kontrol eder.
            break  # Uygulamayı sonlandırır.

        result = graph.invoke({"messages": [("user", user_input)]}, config=config)  # Yeni kullanıcı mesajını aynı conversation thread içerisinde çalıştırır.

        print("\nSemantic Memory:")  # Retrieved semantic memory sonuçlarını göstereceğini belirtir.

        for memory in result.get("semantic_memories", []):  # Retrieved semantic memory kayıtları üzerinde döner.
            print("-", memory)  # Her semantic memory kaydını terminalde gösterir.

        print("\nAgent:", result["messages"][-1].content, "\n")  # Agent'ın son cevabını terminalde gösterir.


if __name__ == "__main__":  # Dosyanın doğrudan çalıştırılıp çalıştırılmadığını kontrol eder.
    main()  # Final State + Memory Agent uygulamasını başlatır.