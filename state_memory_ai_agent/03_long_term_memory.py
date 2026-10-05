"""
Bu uygulama kalıcı Long-Term Memory kullanan basit bir AI Agent oluşturur.

Amaç:
    Conversation Memory ile Long-Term Memory arasındaki farkı göstermek.

Long-Term Memory:
    Kullanıcının açıkça kaydetmek istediği bilgiler JSON dosyasında tutulur.

Kalıcılık:
    Program kapatılıp yeniden açıldığında JSON içerisindeki bilgiler korunur.
"""

import json  # Long-term memory verilerini JSON formatında okumak ve yazmak için kullanılır.
from pathlib import Path  # Memory dosyasının yolunu güvenli şekilde oluşturmak için kullanılır.
from typing import TypedDict  # LangGraph state yapısını tanımlamak için kullanılır.
from langchain_core.messages import HumanMessage, SystemMessage  # Qwen modeline mesaj göndermek için kullanılır.
from langchain_ollama import ChatOllama  # Ollama üzerindeki Qwen modelini kullanmak için kullanılır.
from langgraph.graph import END, START, StateGraph  # Long-term memory workflow'unu oluşturmak için kullanılır.


MODEL = "qwen3:4b"  # Kullanılacak lokal LLM modelini tanımlar.
MEMORY_PATH = Path(__file__).resolve().parent / "data" / "long_term_memory.json"  # Kalıcı memory dosyasının yolunu oluşturur.


class MemoryState(TypedDict):  # Long-term memory graph state yapısını tanımlar.
    user_input: str  # Kullanıcının mevcut mesajını tutar.
    memories: list[str]  # JSON dosyasından yüklenen kalıcı hafızaları tutar.
    memory_saved: bool  # Bu turda yeni bir memory kaydedilip kaydedilmediğini tutar.
    response: str  # Agent'ın kullanıcıya vereceği cevabı tutar.


llm = ChatOllama(model=MODEL, temperature=0)  # Qwen3:4B modelini oluşturur.


def load_memories() -> list[str]:  # JSON dosyasındaki long-term memory kayıtlarını yükler.
    with MEMORY_PATH.open("r", encoding="utf-8") as file:  # Memory dosyasını okuma modunda açar.
        data = json.load(file)  # JSON içeriğini Python nesnesine dönüştürür.
    return data.get("memories", [])  # Memories listesini döndürür.


def save_memory(memory: str) -> None:  # Yeni bilgiyi kalıcı hafızaya yazan yardımcı fonksiyonu tanımlar.
    memories = load_memories()  # Mevcut hafızaları dosyadan yükler.

    if memory not in memories:  # Aynı memory'nin daha önce kaydedilip kaydedilmediğini kontrol eder.
        memories.append(memory)  # Yeni memory'yi listeye ekler.

    with MEMORY_PATH.open("w", encoding="utf-8") as file:  # Memory dosyasını yazma modunda açar.
        json.dump({"memories": memories}, file, ensure_ascii=False, indent=2)  # Güncellenen memory listesini dosyaya kaydeder.


def memory_node(state: MemoryState) -> dict:  # Memory okuma ve yazma işlemini gerçekleştiren graph node'unu tanımlar.
    print("\n[NODE] long_term_memory")  # Eğitim sırasında çalışan memory node'unu gösterir.
    memories = load_memories()  # Daha önce kaydedilmiş kalıcı hafızaları yükler.
    user_input = state["user_input"]  # Kullanıcının mevcut mesajını state'ten alır.
    memory_saved = False  # Başlangıçta yeni memory kaydedilmediğini belirtir.

    if user_input.lower().startswith("hatırla:"):  # Kullanıcının açıkça bilgi kaydetmek isteyip istemediğini kontrol eder.
        memory = user_input.split(":", 1)[1].strip()  # "hatırla:" ifadesinden sonraki bilgi bölümünü çıkarır.
        save_memory(memory)  # Bilgiyi JSON dosyasına kalıcı olarak kaydeder.
        memories = load_memories()  # Güncellenmiş memory listesini tekrar yükler.
        memory_saved = True  # Bu turda hafıza kaydedildiğini state'e bildirir.

    return {"memories": memories, "memory_saved": memory_saved}  # Hafıza durumunu graph state'ine yazar.


def agent_node(state: MemoryState) -> dict:  # Long-term memory bilgilerini kullanarak cevap üreten node'u tanımlar.
    print("[NODE] agent")  # Eğitim sırasında çalışan agent node'unu gösterir.
    memory_text = "\n".join(f"- {memory}" for memory in state["memories"]) or "Kayıtlı bilgi bulunmuyor."  # Memory listesini modele verilecek metne dönüştürür.
    system_prompt = f"""Sen long-term memory kullanan yardımcı bir AI agentsın.

Kalıcı hafızanda bulunan bilgiler:
{memory_text}

Kullanıcının sorusuna yalnızca gerektiğinde bu bilgilerden yararlanarak Türkçe cevap ver.
Kullanıcı 'hatırla:' ile bir bilgi verdiyse ona bilgiyi kaydettiğini söyle."""  # Kalıcı memory'leri Qwen'in context'ine ekleyen system prompt oluşturur.
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=state["user_input"])]  # Qwen'e gönderilecek mesajları oluşturur.
    response = llm.invoke(messages)  # Qwen3:4B ile cevabı üretir.
    return {"response": response.content}  # Agent cevabını graph state'ine yazar.


builder = StateGraph(MemoryState)  # Long-term memory workflow'u için graph oluşturur.
builder.add_node("memory", memory_node)  # Memory node'unu graph'a ekler.
builder.add_node("agent", agent_node)  # Agent node'unu graph'a ekler.
builder.add_edge(START, "memory")  # Önce kalıcı memory'nin yüklenmesini sağlar.
builder.add_edge("memory", "agent")  # Memory bilgisinden sonra agent'ın çalışmasını sağlar.
builder.add_edge("agent", END)  # Agent cevabından sonra graph'ı sonlandırır.
graph = builder.compile()  # Graph'ı çalıştırılabilir hale getirir.


def main() -> None:  # Long-term memory uygulamasını terminalde çalıştırır.
    print("Çıkmak için 'exit' yazın.\n")  # Kullanıcıya çıkış komutunu gösterir.

    while True:  # Kullanıcı ile sürekli etkileşim sağlayan döngüyü başlatır.
        user_input = input("Kullanıcı: ")  # Kullanıcı mesajını alır.

        if user_input.lower() == "exit":  # Çıkış komutunu kontrol eder.
            break  # Uygulamayı sonlandırır.

        initial_state = {"user_input": user_input, "memories": [], "memory_saved": False, "response": ""}  # Graph için başlangıç state'ini oluşturur.
        result = graph.invoke(initial_state)  # Long-term memory graph'ını çalıştırır.
        print("Agent:", result["response"], "\n")  # Agent cevabını gösterir.


if __name__ == "__main__":  # Dosyanın doğrudan çalıştırılmasını kontrol eder.
    main()  # Long-term memory uygulamasını başlatır.