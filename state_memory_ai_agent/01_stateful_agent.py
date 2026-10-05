"""
Bu uygulama LangGraph kullanarak basit bir Stateful AI Agent oluşturur.

Amaç:
    State kavramının LangGraph içerisinde nasıl taşındığını göstermek.

State:
    Kullanıcı girdisi, mevcut görev, çalışma adımı ve agent cevabı tutulur.

Memory:
    Bu örnekte herhangi bir kalıcı veya conversation memory kullanılmaz.
    State yalnızca mevcut graph çalışması boyunca taşınır.
"""

from typing import TypedDict  # LangGraph State yapısını tanımlamak için kullanılır.
from langchain_core.messages import HumanMessage, SystemMessage  # Qwen modeline mesaj göndermek için kullanılır.
from langchain_ollama import ChatOllama  # Ollama üzerindeki Qwen modelini LangChain ile kullanmak için kullanılır.
from langgraph.graph import END, START, StateGraph  # LangGraph graph yapısını oluşturmak için kullanılır.


MODEL = "qwen3:4b"  # Kullanılacak lokal LLM modelini tanımlar.


class AgentState(TypedDict):  # Graph içerisinde node'lar arasında taşınacak state yapısını tanımlar.
    user_input: str  # Kullanıcının verdiği görevi tutar.
    current_task: str  # Agent'ın üzerinde çalıştığı mevcut görevi tutar.
    step_count: int  # Graph içerisinde kaç adım çalışıldığını tutar.
    response: str  # Model tarafından üretilen son cevabı tutar.


llm = ChatOllama(model=MODEL, temperature=0)  # Ollama üzerinde çalışan Qwen3:4B modelini oluşturur.


def prepare_task(state: AgentState) -> dict:  # Kullanıcı girdisini mevcut göreve dönüştüren graph node'unu tanımlar.
    print("\n[NODE] prepare_task")  # Eğitim sırasında çalışan node'u terminalde gösterir.
    return {"current_task": state["user_input"], "step_count": state["step_count"] + 1}  # State içerisindeki görevi ve adım sayısını günceller.


def run_agent(state: AgentState) -> dict:  # Qwen modelini çalıştıran graph node'unu tanımlar.
    print("[NODE] run_agent")  # Eğitim sırasında çalışan node'u terminalde gösterir.
    messages = [SystemMessage(content="Sen yardımcı bir AI agentsın. Kullanıcının görevine kısa ve net Türkçe cevap ver."), HumanMessage(content=state["current_task"])]  # Modele gönderilecek mesajları oluşturur.
    response = llm.invoke(messages)  # Qwen3:4B modelini mevcut görev ile çalıştırır.
    return {"response": response.content, "step_count": state["step_count"] + 1}  # Model cevabını ve yeni adım sayısını state'e yazar.


builder = StateGraph(AgentState)  # AgentState kullanacak LangGraph graph'ını oluşturur.
builder.add_node("prepare_task", prepare_task)  # Görevi hazırlayan node'u graph'a ekler.
builder.add_node("agent", run_agent)  # LLM node'unu graph'a ekler.
builder.add_edge(START, "prepare_task")  # Graph başlangıcını prepare_task node'una bağlar.
builder.add_edge("prepare_task", "agent")  # prepare_task node'unu agent node'una bağlar.
builder.add_edge("agent", END)  # Agent node'undan sonra graph'ı sonlandırır.
graph = builder.compile()  # Tanımlanan graph'ı çalıştırılabilir hale getirir.


def main() -> None:  # Uygulamanın ana fonksiyonunu tanımlar.
    user_input = input("Kullanıcı: ")  # Kullanıcıdan görev alır.
    initial_state = {"user_input": user_input, "current_task": "", "step_count": 0, "response": ""}  # Graph'ın başlangıç state'ini oluşturur.
    result = graph.invoke(initial_state)  # Graph'ı başlangıç state'i ile çalıştırır.
    print("\nAgent:", result["response"])  # Model cevabını terminalde gösterir.
    print("\nFinal State:", result)  # Graph sonunda oluşan state'in tamamını gösterir.


if __name__ == "__main__":  # Dosyanın doğrudan çalıştırılıp çalıştırılmadığını kontrol eder.
    main()  # Uygulamayı başlatır.