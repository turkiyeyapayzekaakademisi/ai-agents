"""
Bu dosyada kullanıcı mesajını doğru specialist agent'a yönlendiren
Supervisor Agent tanımlanır.
"""

from langchain_core.messages import SystemMessage

from config import llm
from state import CustomerServiceState


SUPERVISOR_PROMPT = """
Sen müşteri hizmetleri sisteminin Supervisor Agent'ısın.

Kullanıcı mesajını aşağıdaki üç agent'tan birine yönlendir:

greeting:
Selamlama, teşekkür ve vedalaşma.

faq:
KDV, kargo ücreti, iade, ödeme, şifre, API, giriş ve teknik sorular.

order:
Belirli bir siparişin kargo veya gönderim durumuyla ilgili sorular.

Kısa bir follow-up mesajı geldiyse conversation history ve son çalışan agent'ı dikkate al.

Sadece şu üç değerden birini yaz:
greeting
faq
order
"""


def supervisor_node(state: CustomerServiceState) -> dict:
    last_agent = state.get("last_agent", "yok")

    prompt = (
        SUPERVISOR_PROMPT
        + f"\nSon çalışan specialist agent: {last_agent}"
    )

    response = llm.invoke([
        SystemMessage(content=prompt),
        *state["messages"]
    ])

    decision = response.content.strip().lower()

    if "order" in decision:
        route = "order"
    elif "faq" in decision:
        route = "faq"
    elif "greeting" in decision:
        route = "greeting"
    else:
        route = last_agent if last_agent in {"greeting", "faq", "order"} else "faq"

    print(f"\n[SUPERVISOR] → {route}")

    return {"route": route}