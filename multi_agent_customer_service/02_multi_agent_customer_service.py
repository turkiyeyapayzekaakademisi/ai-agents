"""
Bu uygulama LangGraph kullanarak Multi-Agent müşteri hizmetleri sistemi oluşturur.

Supervisor Agent:
    Kullanıcı mesajını doğru specialist agent'a yönlendirir.

Greeting Agent:
    Selamlama mesajlarını cevaplar.

FAQ Agent:
    Genel ve teknik RAG tool'larını kullanır.

Order Agent:
    Yurt içi ve yurt dışı sipariş tool'larını kullanır.

Memory:
    LangGraph InMemorySaver ile conversation history korunur.
"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agents.faq_agent import faq_agent_node
from agents.greeting_agent import greeting_agent_node
from agents.order_agent import order_agent_node
from agents.supervisor_agent import supervisor_node
from state import CustomerServiceState

from tools.faq_tools import search_general_faq, search_technical_faq
from tools.order_tools import (
    get_domestic_order_status,
    get_international_order_status
)


faq_tools_node = ToolNode([
    search_general_faq,
    search_technical_faq
])


order_tools_node = ToolNode([
    get_domestic_order_status,
    get_international_order_status
])


def supervisor_router(state: CustomerServiceState) -> str:
    return state["route"]


def faq_router(state: CustomerServiceState) -> str:
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "end"


def order_router(state: CustomerServiceState) -> str:
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "end"


builder = StateGraph(CustomerServiceState)


builder.add_node("supervisor", supervisor_node)
builder.add_node("greeting_agent", greeting_agent_node)
builder.add_node("faq_agent", faq_agent_node)
builder.add_node("faq_tools", faq_tools_node)
builder.add_node("order_agent", order_agent_node)
builder.add_node("order_tools", order_tools_node)


builder.add_edge(START, "supervisor")


builder.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "greeting": "greeting_agent",
        "faq": "faq_agent",
        "order": "order_agent"
    }
)


builder.add_edge("greeting_agent", END)


builder.add_conditional_edges(
    "faq_agent",
    faq_router,
    {
        "tools": "faq_tools",
        "end": END
    }
)

builder.add_edge("faq_tools", "faq_agent")


builder.add_conditional_edges(
    "order_agent",
    order_router,
    {
        "tools": "order_tools",
        "end": END
    }
)

builder.add_edge("order_tools", "order_agent")


checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)


def main() -> None:
    config = {
        "configurable": {
            "thread_id": "customer-1"
        }
    }

    print("Multi-Agent Müşteri Hizmetleri")
    print("Çıkmak için 'exit' yazın.\n")

    while True:
        user_input = input("Kullanıcı: ")

        if user_input.lower() == "exit":
            break

        result = graph.invoke(
            {
                "messages": [
                    ("user", user_input)
                ]
            },
            config=config
        )

        print("\nAgent:", result["messages"][-1].content)
        print()


if __name__ == "__main__":
    main()