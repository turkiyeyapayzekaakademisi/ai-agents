"""
Bu dosya ana LLM olan Qwen3:4B modeline
kullanıcı sorusu gönderir.

Model:
    Qwen3:4B

Runtime:
    Ollama

Not:
    Qwen'e ekonomi hakkında konuşmaması gerektiğini
    özellikle söylemiyoruz.

Bunun sebebi Output Guardrail'in gerçekten
çalıştığını göstermek istememizdir.
"""

from ollama import chat

from config import MAIN_LLM_MODEL


def generate_answer(
    user_prompt: str
) -> str:

    # Ollama üzerindeki Qwen modeline
    # kullanıcı sorusunu gönder.
    response = chat(
        model=MAIN_LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant. "
                    "Answer the user's question clearly "
                    "and concisely. "
                    "Answer in English."
                )
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    )

    # Model cevabını döndür.
    return response.message.content