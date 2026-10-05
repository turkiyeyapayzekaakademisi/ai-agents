"""
Bu uygulama LangGraph kullanarak Conversation Memory kullanan bir AI Agent oluşturur.

Amaç:
    Aynı conversation/thread içerisindeki geçmiş mesajların korunmasını göstermek.

Memory:
    InMemorySaver kullanılarak konuşma geçmişi RAM üzerinde tutulur.

Önemli:
    Program kapatıldığında InMemorySaver içerisindeki conversation memory silinir.
"""

from langchain_core.messages import SystemMessage  # Agent'a sistem talimatı göndermek için kullanılır.
from langchain_ollama import ChatOllama  # Ollama üzerindeki Qwen modelini kullanmak için kullanılır.
from langgraph.checkpoint.memory import InMemorySaver  # Conversation state'ini thread bazında RAM'de tutmak için kullanılır.
from langgraph.graph import END, START, MessagesState, StateGraph  # Mesaj tabanlı LangGraph state yapısını oluşturmak için kullanılır.


MODEL = "qwen3:4b"  # Kullanılacak lokal LLM modelini tanımlar.
THREAD_ID = "conversation-1"  # Aynı konuşmayı tanımlamak için kullanılacak thread kimliğini belirler.


llm = ChatOllama(model=MODEL, temperature=0)  # Qwen3:4B modelini oluşturur.
checkpointer = InMemorySaver()  # Thread state'lerini RAM üzerinde saklayan checkpointer oluşturur.


def call_model(state: MessagesState) -> dict:  # Conversation state'i kullanarak modeli çalıştıran node'u tanımlar.
    messages = [SystemMessage(content="Sen conversation memory kullanan yardımcı bir AI agentsın. Önceki konuşmaları dikkate alarak Türkçe cevap ver."), *state["messages"]]  # System mesajını konuşma geçmişinin önüne ekler.
    response = llm.invoke(messages)  # Qwen modelini bütün mevcut conversation history ile çalıştırır.
    return {"messages": [response]}  # Yeni assistant mesajını LangGraph state'ine ekler.


builder = StateGraph(MessagesState)  # Mesaj geçmişini state olarak taşıyan graph oluşturur.
builder.add_node("agent", call_model)  # Qwen modelini çağıran agent node'unu ekler.
builder.add_edge(START, "agent")  # Graph başlangıcını agent node'una bağlar.
builder.add_edge("agent", END)  # Agent cevabından sonra graph'ı bitirir.
graph = builder.compile(checkpointer=checkpointer)  # Graph'ı conversation memory sağlayan checkpointer ile derler.


def main() -> None:  # Terminal tabanlı conversation uygulamasını çalıştırır.
    config = {"configurable": {"thread_id": THREAD_ID}}  # Aynı konuşmayı devam ettirmek için thread_id tanımlar.
    print("Çıkmak için 'exit' yazın.\n")  # Kullanıcıya çıkış komutunu gösterir.

    while True:  # Çok turlu konuşmanın devam etmesini sağlar.
        user_input = input("Kullanıcı: ")  # Kullanıcıdan yeni mesaj alır.

        if user_input.lower() == "exit":  # Kullanıcının uygulamadan çıkmak isteyip istemediğini kontrol eder.
            break  # Conversation döngüsünü sonlandırır.

        result = graph.invoke({"messages": [("user", user_input)]}, config=config)  # Yalnızca yeni mesajı gönderir; eski mesajlar checkpointer'dan yüklenir.
        print("Agent:", result["messages"][-1].content, "\n")  # Agent'ın son cevabını terminalde gösterir.


if __name__ == "__main__":  # Dosya doğrudan çalıştırıldığında kontrol sağlar.
    main()  # Conversation uygulamasını başlatır.