"""
Bu dosyada selamlama ve vedalaşma mesajlarını yöneten Greeting Agent bulunur.
"""

from langchain_core.messages import SystemMessage

from config import llm
from state import CustomerServiceState


GREETING_PROMPT = """
Sen müşteri hizmetlerinin Greeting Agent'ısın.

Selamlama, teşekkür ve vedalaşma mesajlarına
kısa, doğal ve Türkçe cevap ver.

Şirket veya sipariş bilgisi uydurma.
"""


def greeting_agent_node(state: CustomerServiceState) -> dict:
    print("[AGENT] Greeting Agent")

    response = llm.invoke([
        SystemMessage(content=GREETING_PROMPT),
        *state["messages"]
    ])

    return {
        "messages": [response],
        "last_agent": "greeting"
    }