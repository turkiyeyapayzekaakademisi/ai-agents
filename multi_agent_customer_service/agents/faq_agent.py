"""
Bu dosyada genel ve teknik FAQ RAG tool'larını kullanan FAQ Agent bulunur.
"""

from langchain_core.messages import SystemMessage

from config import llm
from state import CustomerServiceState
from tools.faq_tools import search_general_faq, search_technical_faq


FAQ_PROMPT = """
Sen şirketin FAQ Agent'ısın.

İki tool kullanabilirsin:

search_general_faq:
KDV, kargo ücreti, ödeme, iade ve genel şirket politikaları.

search_technical_faq:
Şifre, giriş, API, mobil uygulama ve teknik konular.

Kullanıcının sorusuna uygun tool'u seç ve mutlaka bilgi kaynağından veri getir.

Tool sonucunda bulunmayan şirket bilgisini uydurma.

Tool sonucu geldikten sonra kullanıcıya kısa ve Türkçe cevap ver.
"""


faq_llm = llm.bind_tools([
    search_general_faq,
    search_technical_faq
])


def faq_agent_node(state: CustomerServiceState) -> dict:
    print("[AGENT] FAQ Agent")

    response = faq_llm.invoke([
        SystemMessage(content=FAQ_PROMPT),
        *state["messages"]
    ])

    return {
        "messages": [response],
        "last_agent": "faq"
    }