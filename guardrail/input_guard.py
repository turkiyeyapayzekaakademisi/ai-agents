"""
Bu dosya Input Guardrail katmanını oluşturur.

Model:
    Meta Llama Prompt Guard 2 86M

Amaç:
    Kullanıcı prompt'u içerisinde prompt injection
    veya jailbreak girişimi bulunup bulunmadığını kontrol etmek.

Akış:

    Kullanıcı Prompt'u
            ↓
    Meta Prompt Guard 2
            ↓
      BENIGN / MALICIOUS
            ↓
        İzin / Engelle
"""

import torch

from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer

from config import INPUT_GUARD_THRESHOLD
from config import PROMPT_GUARD_MODEL


class InputGuard:

    def __init__(self):

        print("\n[INPUT GUARD]")
        print("Meta Prompt Guard 2 yükleniyor...")

        # GPU varsa CUDA kullan.
        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        # Tokenizer yükle.
        self.tokenizer = AutoTokenizer.from_pretrained(
            PROMPT_GUARD_MODEL
        )

        # Sequence Classification modeli yükle.
        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(
                PROMPT_GUARD_MODEL
            )
        )

        # Modeli CPU veya GPU'ya taşı.
        self.model.to(
            self.device
        )

        # Inference moduna geçir.
        self.model.eval()

        print(
            f"Meta Prompt Guard hazır. "
            f"Device: {self.device}"
        )


    def check(
        self,
        text: str
    ) -> dict:

        # Kullanıcı metnini tokenize et.
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        # Tensor'ları modelin bulunduğu cihaza taşı.
        inputs = inputs.to(
            self.device
        )

        # Gradient hesaplamadan inference yap.
        with torch.no_grad():

            outputs = self.model(
                **inputs
            )

        # Modelin ham classification skorları.
        logits = outputs.logits[0]

        # Skorları olasılığa çevir.
        probabilities = torch.softmax(
            logits,
            dim=-1
        )

        # En yüksek olasılığa sahip sınıfı bul.
        predicted_class = int(
            torch.argmax(
                probabilities
            ).item()
        )

        # Model label bilgisini al.
        label = (
            self.model.config.id2label
            .get(
                predicted_class,
                f"LABEL_{predicted_class}"
            )
        )

        # Bazı config sürümlerinde label isimleri
        # LABEL_0 / LABEL_1 şeklinde gelebilir.
        label_mapping = {
            "LABEL_0": "BENIGN",
            "LABEL_1": "MALICIOUS",
            "BENIGN": "BENIGN",
            "MALICIOUS": "MALICIOUS"
        }

        label = label_mapping.get(
            label.upper(),
            label.upper()
        )

        # Tahmin edilen sınıfın güven skoru.
        score = float(
            probabilities[
                predicted_class
            ].item()
        )

        # MALICIOUS ise ve threshold üzerindeyse engelle.
        blocked = (
            label == "MALICIOUS"
            and
            score >= INPUT_GUARD_THRESHOLD
        )

        return {
            "label": label,
            "score": score,
            "blocked": blocked
        }