"""
Bu dosya Output Guardrail katmanını oluşturur.

Model:
    Google ShieldGemma 2B

Amaç:
    Qwen tarafından oluşturulan cevabın
    tanımlanan ekonomi ve finans politikasını
    ihlal edip etmediğini kontrol etmek.

Akış:

    Kullanıcı Prompt'u
            +
      Qwen Cevabı
            +
          Policy
            ↓
       ShieldGemma
            ↓
         YES / NO

YES:
    Policy ihlali var.

NO:
    Policy ihlali yok.
"""

import torch

from transformers import AutoModelForCausalLM
from transformers import AutoTokenizer

from config import OUTPUT_GUARD_THRESHOLD
from config import OUTPUT_POLICY
from config import SHIELD_GEMMA_MODEL


class OutputGuard:

    def __init__(self):

        print("\n[OUTPUT GUARD]")
        print("ShieldGemma yükleniyor...")

        # GPU kontrolü.
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        # GPU kullanılıyorsa daha az memory
        # kullanmak için uygun dtype seç.
        if self.device == "cuda":

            if torch.cuda.is_bf16_supported():

                self.dtype = torch.bfloat16

            else:

                self.dtype = torch.float16

        else:

            self.dtype = torch.float32

        # Tokenizer.
        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                SHIELD_GEMMA_MODEL
            )
        )

        # ShieldGemma modelini yükle.
        self.model = (
            AutoModelForCausalLM
            .from_pretrained(
                SHIELD_GEMMA_MODEL,
                torch_dtype=self.dtype,
                low_cpu_mem_usage=True
            )
        )

        # Modeli ilgili cihaza taşı.
        self.model.to(
            self.device
        )

        # Inference mode.
        self.model.eval()

        print(
            f"ShieldGemma hazır. "
            f"Device: {self.device}"
        )


    def check(
        self,
        user_prompt: str,
        assistant_response: str
    ) -> dict:

        # Kullanıcı ve assistant konuşmasını oluştur.
        #
        # Son mesaj assistant olduğu için ShieldGemma
        # assistant cevabını policy açısından değerlendirir.
        chat = [
            {
                "role": "user",
                "content": user_prompt
            },
            {
                "role": "assistant",
                "content": assistant_response
            }
        ]

        # ShieldGemma'nın kendi chat template'ini
        # ve bizim policy'mizi kullan.
        inputs = (
            self.tokenizer.apply_chat_template(
                chat,
                guideline=OUTPUT_POLICY,
                return_tensors="pt",
                return_dict=True
            )
        )

        # Tensor'ları modele taşı.
        inputs = inputs.to(
            self.device
        )

        # Forward pass.
        with torch.no_grad():

            outputs = self.model(
                **inputs
            )

        # Sonraki token için model logits.
        logits = outputs.logits[
            0,
            -1
        ]

        # Vocabulary.
        vocab = (
            self.tokenizer.get_vocab()
        )

        # ShieldGemma cevaplarını
        # Yes / No üzerinden skorlar.
        yes_token_id = vocab["Yes"]

        no_token_id = vocab["No"]

        # Sadece Yes ve No token skorlarını al.
        selected_logits = logits[
            [
                yes_token_id,
                no_token_id
            ]
        ]

        # Probability hesapla.
        probabilities = torch.softmax(
            selected_logits,
            dim=0
        )

        # Yes = policy violation.
        violation_score = float(
            probabilities[0].item()
        )

        # No = policy violation yok.
        safe_score = float(
            probabilities[1].item()
        )

        # Violation threshold üzerindeyse engelle.
        blocked = (
            violation_score
            >=
            OUTPUT_GUARD_THRESHOLD
        )

        return {
            "violation_score": violation_score,
            "safe_score": safe_score,
            "blocked": blocked
        }