"""
Bu dosyada AI Agent uygulamasının nihai Structured Output modeli tanımlanır.

OrderResult:
    Qwen3 modelinin görev tamamlandıktan sonra üreteceği
    yapılandırılmış sipariş sonucunu tanımlar.
"""

from typing import Literal
from pydantic import BaseModel, Field


class OrderResult(BaseModel):
    order_id: str = Field(description="İşlem yapılan sipariş numarası.")
    status: Literal["hazirlaniyor", "kargoya_verildi", "iptal_edildi", "bulunamadi"] = Field(description="Siparişin gerçek mevcut durumu.")
    message: str = Field(description="Kullanıcıya gösterilecek Türkçe açıklama.")