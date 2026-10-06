"""
Bu dosyada yurt içi ve yurt dışı sipariş tool'larını kullanan Order Agent bulunur.
"""

from langchain_core.messages import SystemMessage

from config import llm
from state import CustomerServiceState
from tools.order_tools import (
    get_domestic_order_status,
    get_international_order_status
)


ORDER_PROMPT = """
Sen şirketin Order Agent'ısın.

İki tool kullanabilirsin:

get_domestic_order_status:
Yurt içi siparişleri sorgular.

get_international_order_status:
Yurt dışı siparişleri sorgular.

Kurallar:

- Kullanıcı yurt içi diyorsa domestic tool kullan.
- Kullanıcı yurt dışı diyorsa international tool kullan.
- Sipariş numarasını conversation history'den de kullanabilirsin.
- Siparişin yurt içi mi yurt dışı mı olduğu bilinmiyorsa tool çağırma.
- Böyle bir durumda kullanıcıya sadece:
  "Siparişiniz yurt içi mi yoksa yurt dışı mı?"
  diye sor.
- Sipariş bilgilerini tahmin etme.
- Tool sonucu geldikten sonra kısa ve Türkçe cevap ver.
"""


order_llm = llm.bind_tools([
    get_domestic_order_status,
    get_international_order_status
])


def order_agent_node(state: CustomerServiceState) -> dict:
    print("[AGENT] Order Agent")

    response = order_llm.invoke([
        SystemMessage(content=ORDER_PROMPT),
        *state["messages"]
    ])

    return {
        "messages": [response],
        "last_agent": "order"
    }