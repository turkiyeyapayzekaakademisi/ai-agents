"""
Bu uygulama Ollama üzerinde çalışan Qwen3:4B modeli ile temel bir AI Agent oluşturur.

Agent:
    Kullanıcının sipariş talebini değerlendirir.

Tools:
    get_order_status ile siparişin gerçek durumunu öğrenir.
    cancel_order ile uygun siparişi iptal eder.

Agent Loop:
    Model bir tool çağırdığında Python fonksiyonu çalıştırılır.
    Tool sonucu tekrar modele gönderilir.
    Model görev tamamlanana kadar yeni tool çağrıları yapabilir.

Structured Output:
    Görev tamamlandıktan sonra Qwen3 nihai cevabı OrderResult şemasına göre üretir.
"""

import json
from ollama import chat
from models import OrderResult
from tools import cancel_order, get_order_status


MODEL = "qwen3:4b"
MAX_STEPS = 5


SYSTEM_PROMPT = """
Sen bir sipariş yönetim agentısın.

Siparişlerle ilgili hiçbir bilgiyi tahmin etme.
Sipariş durumunu öğrenmek için her zaman get_order_status aracını kullan.

Kullanıcı yalnızca sipariş durumunu soruyorsa:
- get_order_status kullan.
- Siparişi iptal etme.

Kullanıcı sipariş iptali istiyorsa:
- Önce get_order_status kullan.
- Sipariş hazirlaniyor durumundaysa cancel_order kullan.
- Sipariş kargoya_verildi durumundaysa iptal etme.

Tool sonuçlarında bulunmayan bilgi üretme.
"""


TOOLS = [get_order_status, cancel_order]


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Model tarafından çağrılan tool'u çalıştırır."""

    if tool_name == "get_order_status":
        return get_order_status(**arguments)

    if tool_name == "cancel_order":
        return cancel_order(**arguments)

    return json.dumps({"error": "Bilinmeyen tool."}, ensure_ascii=False)


def run_agent(user_input: str) -> OrderResult:
    """Kullanıcı isteğini Agent Loop içerisinde çalıştırır."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

    for _ in range(MAX_STEPS):
        response = chat(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            think=False
        )

        messages.append(response.message)

        if not response.message.tool_calls:
            break

        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments
            tool_result = execute_tool(tool_name, arguments)

            messages.append({
                "role": "tool",
                "tool_name": tool_name,
                "content": tool_result
            })

    final_response = chat(
        model=MODEL,
        messages=messages + [{
            "role": "user",
            "content": "Görevin nihai sonucunu yalnızca tool sonuçlarına dayanarak yapılandırılmış formatta üret."
        }],
        format=OrderResult.model_json_schema(),
        think=False
    )

    return OrderResult.model_validate_json(final_response.message.content)


def main() -> None:
    """Terminalden kullanıcı isteğini alır ve agent sonucunu gösterir."""

    user_input = input("Kullanıcı: ")
    result = run_agent(user_input)

    print("\nAgent Sonucu:")
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()


"""
ORD-1001 siparişimin durumunu kontrol et.
ORD-1001 siparişim henüz kargoya verilmediyse iptal et.
ORD-1002 siparişimi iptal et.
"""