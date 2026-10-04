"""
Bu dosyada AI Agent'ın kullanabileceği sipariş araçları tanımlanır.

get_order_status:
    Siparişin gerçek durumunu getirir.

cancel_order:
    Sipariş hazırlanıyorsa iptal eder.
    Kargoya verilmiş siparişi iptal etmez.
"""

import json
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent / "data" / "orders.json"


def load_orders() -> dict:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_orders(orders: dict) -> None:
    with DATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(orders, file, ensure_ascii=False, indent=2)


def get_order_status(order_id: str) -> str:
    """Belirtilen sipariş numarasının mevcut durumunu getirir."""

    print(f"\n[TOOL] get_order_status({order_id})")

    orders = load_orders()
    order = orders.get(order_id)

    if order is None:
        return json.dumps({
            "order_id": order_id,
            "status": "bulunamadi",
            "message": "Sipariş bulunamadı."
        }, ensure_ascii=False)

    return json.dumps({
        "order_id": order_id,
        "urun": order["urun"],
        "status": order["durum"]
    }, ensure_ascii=False)


def cancel_order(order_id: str) -> str:
    """Sipariş hazırlanıyorsa iptal eder."""

    print(f"\n[TOOL] cancel_order({order_id})")

    orders = load_orders()
    order = orders.get(order_id)

    if order is None:
        return json.dumps({
            "order_id": order_id,
            "status": "bulunamadi",
            "message": "Sipariş bulunamadı."
        }, ensure_ascii=False)

    if order["durum"] == "kargoya_verildi":
        return json.dumps({
            "order_id": order_id,
            "status": "kargoya_verildi",
            "message": "Sipariş kargoya verildiği için iptal edilemez."
        }, ensure_ascii=False)

    if order["durum"] == "iptal_edildi":
        return json.dumps({
            "order_id": order_id,
            "status": "iptal_edildi",
            "message": "Sipariş zaten iptal edilmiş."
        }, ensure_ascii=False)

    order["durum"] = "iptal_edildi"
    save_orders(orders)

    return json.dumps({
        "order_id": order_id,
        "status": "iptal_edildi",
        "message": "Sipariş başarıyla iptal edildi."
    }, ensure_ascii=False)