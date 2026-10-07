"""
Bu dosya projede kullanılacak model isimlerini,
guardrail threshold değerlerini ve güvenlik politikasını içerir.

Modeller:
    Input Guardrail  -> Meta Prompt Guard 2
    Ana LLM          -> Qwen3:4B
    Output Guardrail -> Google ShieldGemma

Politika:
    AI sistemi ekonomi ve finans hakkında cevap vermemelidir.
"""


# =========================================================
# MODELLER
# =========================================================

PROMPT_GUARD_MODEL = "meta-llama/Llama-Prompt-Guard-2-86M"
# PROMPT_GUARD_MODEL = "protectai/deberta-v3-base-prompt-injection-v2"

SHIELD_GEMMA_MODEL = "google/shieldgemma-2b"

MAIN_LLM_MODEL = "qwen3:4b"


# =========================================================
# THRESHOLD
# =========================================================

INPUT_GUARD_THRESHOLD = 0.50

OUTPUT_GUARD_THRESHOLD = 0.50


# =========================================================
# OUTPUT POLICY
# =========================================================

OUTPUT_POLICY = """
"No Economics or Finance":

The assistant response must not provide information,
explanations, analysis, advice or recommendations about
economics or finance.

This includes topics such as:

- inflation
- interest rates
- monetary policy
- economic growth
- unemployment
- currencies
- banking
- investing
- stocks
- bonds
- cryptocurrencies
- financial markets

If the assistant response discusses these topics,
the response violates this policy.
"""